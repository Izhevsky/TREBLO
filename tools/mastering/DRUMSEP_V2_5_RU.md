# TREBLO Astra Audio v2.5 — SHA-verified 6-stem DrumSep (experimental)

**Статус:** код адаптера испытан на синтетических ответах модели; настоящий checkpoint в этой сессии НЕ загружен и реальный Golden Teeth neural master **не создан**. Это не финальный FLAC релиз.

## Новое в v2.5

Вместо недоступного по первоначальной ссылке 5-stem checkpoint, используется **6-stem DrumSep** из проекта [openmirlab/mdxnet-infer](https://github.com/openmirlab/mdxnet-infer). Разработчики проверили byte-identical модели по двум зеркалам и разместили у себя на GitHub Release; библиотека проверяет SHA-256 checkpoint и config при загрузке. ВАЖНО: модель и код — разные лицензии. Лицензия оригинальных весов авторами не документирована, не использовать их коммерчески без отдельного разрешения. На текущий момент веса не включены в TREBLO.

- **6 neural outputs:** `kick`, `snare`, `toms`, `hh`, `ride`, `crash`.
- Для совместимости с TREBLO v2.4: `cymbals = ride + crash`, затем 5 float32 WAV.
- Прямой Python API вместо CLI, потому что `mdxnet-infer` CLI сохраняет WAV в **PCM16**, а нам важно не выполнять лишнее промежуточное квантование.
- Входной `drums golden teeth.wav` — 44 100 Гц, Stereo, PCM16, 10 553 345 кадров; SHA-256 `77b959343845fe07d6b17cf8a25ee27b3fb9dfb79f33d0fa939bc4c7dbffd3a7`.
- Выходы содержат только **нейросетевые предсказания**, без новых ударов, эквализации, дополнительного лимитера, дополнительного битового шума и перезаписи оригинала.
- Без скрытых загрузок: требуется явно разрешить `--allow-download`. Режим `--dry-run` не качает модель и не обрабатывает звук.
- Валидируются входные данные, точность сетки, NaN/Inf, размерность, SHA-256 исходника и контрольная сумма результата.
- Перезапись существующих выходных стемов запрещена.

## Установка (Windows PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install "mdxnet-infer @ git+https://github.com/openmirlab/mdxnet-infer.git"
pip install soundfile numpy
```

Для воспроизводимости production-окружения закрепите конкретный проверенный commit SHA пакета `mdxnet-infer` вместо плавающей ветки GitHub. Источник весов и две SHA-256 пары встроены в `drumsep_6stem_float_bridge.py`.

**Проверочный запуск, никакой загрузки:**

```powershell
python tools/mastering/drumsep_6stem_float_bridge.py --input "C:\Audio\drums golden teeth.wav" --output-dir "C:\Audio\NeuralOut" --dry-run
```

**Реальная модель:**

```powershell
python tools/mastering/drumsep_6stem_float_bridge.py --input "C:\Audio\drums golden teeth.wav" --output-dir "C:\Audio\NeuralOut" --cache-dir "C:\Audio\MSST_ModelCache" --device cpu --allow-download
```

Для NVIDIA GPU заменить `--device cpu` на `--device cuda` (нужна совместимая CUDA-сборка PyTorch). Публиковать оригинальный WAV в GitHub или ином публичном месте **не нужно**: инференс локальный, из сети забираются только публичные веса.

## Что получается

```
NeuralOut/
  drums golden teeth/
    kick.wav        (FLOAT32)
    snare.wav       (FLOAT32)
    toms.wav        (FLOAT32)
    hh.wav          (FLOAT32)
    cymbals.wav     (FLOAT32; ride + crash)
    INFERENCE_REPORT.json
```

**Следующий шаг:** просмотреть сумму предсказанных стемов, остаток `drums - sum(predicted)`, артефакты хэтов, клэпа и тарелок; затем запустить существующий модуль `neural_drumsep_bridge.py delta` из v2.4 — он отклонит некорректный результат. Только после этого можно собирать `original + delta`, выполнять Astra QC и получать A/B с Golden Teeth Studio Rework/v2.3. НИ ОДИН ИЗ ЭТИХ ДЕЙСТВИЙ НЕ ЗАЯВЛЕН КАК ВЫПОЛНЕННЫЙ ДЛЯ РЕАЛЬНЫХ НЕЙРОСТЕМОВ.

### Команда для второй стадии

```powershell
python tools/mastering/neural_drumsep_bridge.py delta --drums "C:\Audio\drums golden teeth.wav" --predicted-dir "C:\Audio\NeuralOut" --file-stem "drums golden teeth" --output "C:\Audio\work\drum_delta.wav" --report "C:\Audio\work\drum_delta_qc.json"
```

Стемы Golden Teeth являются собственностью пользователя, **не должны** загружаться в публичные workflow GitHub Actions без отдельного согласия.

## Инженерные ограничения

1. Расхождение суммы предсказаний с входом не гарантирует плохого разделения, а малое расхождение не гарантирует чистоты hi-hat: проверять остаток и bleed.
2. PCM24 master производится только из отдельного float32-премастера по Astra Codex Standard с финальным true-peak контролем. Получившиеся float32 нейростемы не являются мастерингом.
3. Код с checkpoint, загружаемым через PyTorch, запускается только для заранее проверенных SHA-256 файлов в доверенной среде. Не подгружайте неизвестные `.ckpt`.
4. Лицензия 6-stem checkpoint не подтверждена оригинальными авторами. Если TREBLO станет коммерческим сервисом, до этого требуются явные права на модель.
5. До настоящего инференса и A/B со слушателем **не делать заявлений о повышении качества звука**.

## Тесты

```bash
python -m unittest discover -s tests -p 'test_drumsep_6stem_float_bridge.py' -v
```

Восемь тестов проверяют вызов mock-предсказаний, float32-экспорт, SHA-256, запрет перезаписи, отсутствие скрытой загрузки, неподходящие формат/сетки и чистоту ошибок. Они НЕ проверяют качество настоящей модели.

Источники: https://github.com/openmirlab/mdxnet-infer ; https://github.com/ZFTurbo/Music-Source-Separation-Training .