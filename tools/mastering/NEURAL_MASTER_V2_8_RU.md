# TREBLO / Astra Audio v2.8 — Neural Kick End-to-End (эксперимент)

**Результат этапа:** создан единый рабочий пайплайн, выполняющий preflight → реальный DrumSep inference (если веса доступны) → guard пяти нейростемов → только +0…+0,35 dB kick → float32 premaster −6 dBFS sample peak → 4× SoXR / FFmpeg limiter → FLAC24/FLAC16 → A/B с Studio Rework и v2.3. 

**Фактический статус на 01.11.2026:** реальный DrumSep уже успешно запущен на синтетических барабанах в GitHub Actions (#9/#10). Но текущая локальная аудиосреда не может скачать модельные веса; на Golden Teeth _реальный нейросетевой инференс не выполнен_. В этом пакете **нет нового музыкального Neural DrumSep FLAC**. Есть отчёт о проверке подлинных исходников и воспроизводимый код. 8/8 CPU тестов с синтетическими *псевдопредсказаниями*, но настоящим DSP/FFmpeg/FLAC рендером. Эти тесты не доказывают качество нейросети.

## Почему это следующий шаг

Предыдущий v2.7 показал на известных синтетических барабанах: SI-SDR kick +27,07 dB, toms +22,29, snare +7,43, hi-hat −0,66, crash −2,47, ride −26,48 dB. **Это результаты только синтетики**, нельзя автоматически переносить их на Golden Teeth. Поэтому мы не меняем нейросетевые HH/snare/toms/cymbals, сохраняем v2.3 как базу. Малую коррекцию kick допускаем только если соблюдена погрешность суммирования и энергетический бюджет.

## Источники Golden Teeth

| Роль | Имя | Ограничение |
|---|---|---|
| Основной drums-стем | `drums golden teeth.wav` | 44.1k stereo PCM16 |
| Неотлимитированный базовый микс | `GT_v23_raw_float.wav` | **FLOAT**, не готовый v2.3 FLAC |
| Референс 1 | `Golden_Teeth_Transient_Precision_v2_3_24bit.flac` | только для A/B |
| Референс 2 | `GT_Studio_Rework_MASTER.flac` | любимый музыкальный эталон, только A/B |

Все имеют 10 553 345 кадров и 44 100 Гц. В `output/golden_teeth_v28_preflight.json` — точные SHA-256 всех четырёх. Исходники НЕ копируются в репозиторий и не перезаписываются.

## Установка Windows

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install numpy scipy soundfile pedalboard
python -m pip install "mdxnet-infer @ git+https://github.com/openmirlab/mdxnet-infer.git@cb4779eedeca4f55ba498df8e234e2b5f4b90aaf"
ffmpeg -version
```

Проверить наличие FFmpeg с `soxr`. Для CPU требуются дополнительные ресурсы; на GPU допустим `--device cuda`, если совместимая сборка PyTorch и драйвер доступны.

## Команды (подставить реальные пути, **никогда не загружать WAV в публичный GitHub**)

```powershell
python tools/mastering/neural_master_pipeline.py preflight `
  --drums "C:\Audio\drums golden teeth.wav" `
  --v23-unlimited "C:\Audio\GT_v23_raw_float.wav" `
  --v23-master "C:\Audio\Golden_Teeth_Transient_Precision_v2_3_24bit.flac" `
  --studio-rework "C:\Audio\GT_Studio_Rework_MASTER.flac"

# Реальная модель DrumSep; явно разрешённая загрузка 438MB SHA-проверенных весов.
python tools/mastering/neural_master_pipeline.py infer `
  --drums "C:\Audio\drums golden teeth.wav" `
  --output-dir "C:\Audio\neural_output" `
  --cache-dir "C:\Audio\models" `
  --device cpu --allow-download

# Только ПОСЛЕ реального инференса, в новой рабочей папке.
python tools/mastering/neural_master_pipeline.py render `
  --drums "C:\Audio\drums golden teeth.wav" `
  --v23-unlimited "C:\Audio\GT_v23_raw_float.wav" `
  --v23-master "C:\Audio\Golden_Teeth_Transient_Precision_v2_3_24bit.flac" `
  --studio-rework "C:\Audio\GT_Studio_Rework_MASTER.flac" `
  --neural-dir "C:\Audio\neural_output\drums golden teeth" `
  --workdir "C:\Audio\experiments\v28_neural_kick" `
  --kick-db 0.25 --target-lufs -13.7 --true-peak -1.4
```

`infer` использует `drumsep_6stem_float_bridge` и при успехе сохраняет пять Float32 WAV (kick, snare, toms, hh, cymbals) плюс отчет. `render` отвергает недостающие файлы, несоответствие сетки, чрезмерную разницу, подозрительное суммирование, выход за лимит True Peak, неверную разрядность базового микса и попытку перезаписи. Все стемы должны быть **реально получены моделью**; фиктивные данные нужны исключительно в тестах.

В каталоге эксперимента: `NEURAL_KICK_PREMASTER_float32.wav`, `Golden_Teeth_Neural_Kick_CANDIDATE_24bit.flac`, 16-битный FLAC, два A/B и `REPORT.json`. A/B имеют известный порядок, это не слепой тест. Превосходство на слух **не подтверждено**.

**Лицензия весов DrumSep не доказана для коммерческого использования**. Код mdxnet-infer MIT, но это не разрешение использовать обученные веса в платном сервисе. До подтверждения лицензии — только частные исследования; веса не помещать в публичные ZIP/GitHub.

## Автотесты

```bash
PYTHONPATH=tools/mastering python -m unittest discover -s tests -p 'test_neural_master_pipeline.py' -v
```

Покрывает полный синтетический путь до FLAC, формат и число кадров, лимитер, немодификацию источников, отказ при отсутствующих прогнозах и выходе gain за пределы. Настоящая нейросеть в CI v2.8 НЕ запускается — проверяется в отдельном real-checkpoint CPU бенчмарке v2.6/v2.7.