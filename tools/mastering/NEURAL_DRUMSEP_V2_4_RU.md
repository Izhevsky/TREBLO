# TREBLO / Astra Audio v2.4 — Neural DrumSep Integration (готовность к запуску)

## Статус и ограничение

Подготовлен **исполняемый адаптер для настоящего MDX23C DrumSep, но сама обученная модель в этом окружении НЕ запущена**. Веса недоступны для скачивания в текущей среде: прямой доступ к GitHub/Hugging Face через рабочий контейнер заблокирован. Заявления о качестве нейросетевого разделения и мастер v2.4 из настоящих ML-стемов **пока отсутствуют**.

Это не повторение v2.2-варианта с частотно-временными масками. `inference` вызывает **официальный `inference.py` из MSST**, после чего `delta` требует пять **реально созданных нейросетью** WAV: `kick.wav`, `snare.wav`, `toms.wav`, `hh.wav`, `cymbals.wav`.

## Выбранная модель

MDX23C DrumSep 5-stem (jarredou): kick, snare, toms, hi-hat, cymbals.

- Модуль MSST: https://github.com/ZFTurbo/Music-Source-Separation-Training
- Совместимая конфигурация: https://github.com/jarredou/models/releases/download/DrumSep/config_mdx23c.yaml
- Веса: https://github.com/jarredou/models/releases/download/DrumSep/drumsep_5stems_mdx23c_jarredou.ckpt

Веса имеют размер около 417 МиБ (в зависимости от источника) и намеренно **не входят** в ZIP/GitHub. Скачивать и использовать веса только из доверенного источника; `torch.load` внутри upstream использует `weights_only=False`, что позволяет исполнять код при загрузке небезопасного checkpoint. Принимать только доверенные файлы, сверять SHA-256.

**Для Golden Teeth** входной `drums golden teeth.wav` имеет 44.1 kHz, stereo, 3:59.305 — не нужен новый пересчёт частоты перед инференсом. В папке для MSST лучше положить только одну копию с простым именем `drums.wav`.

## Windows — подготовка

1. Установить Python 3.11/3.12, FFmpeg, PyTorch (выбранный CPU/CUDA), зависимости MSST согласно upstream README. Для GPU — подходящий CUDA/PyTorch.
2. `git clone https://github.com/ZFTurbo/Music-Source-Separation-Training.git C:\\Tools\\MSST`
3. Скачать указанные конфигурацию и `.ckpt` в `C:\\Models\\DrumSep\\`.
4. Создать `C:\\Audio\\GT\\input\\drums.wav` из исходного `drums golden teeth.wav` (не заменять оригинал).
5. Установить `numpy`, `soundfile` для нашей QC-обёртки.

```powershell
python tools/mastering/neural_drumsep_bridge.py inference `
  --msst-repo C:\Tools\MSST `
  --config C:\Models\DrumSep\config_mdx23c.yaml `
  --checkpoint C:\Models\DrumSep\drumsep_5stems_mdx23c_jarredou.ckpt `
  --input-dir C:\Audio\GT\input `
  --output-dir C:\Audio\GT\neural `
  --dry-run
```

При корректной подготовке убрать `--dry-run`. Если GPU нет, добавить `--cpu`. **GPU рекомендуется**, поскольку полноценный прогон на CPU может быть очень медленным.

### Только после появления настоящих neural WAV

```powershell
python tools/mastering/neural_drumsep_bridge.py delta `
  --drums C:\Audio\GT\input\drums.wav `
  --predicted-dir C:\Audio\GT\neural `
  --file-stem drums `
  --output C:\Audio\GT\work\drum_neural_delta_float32.wav `
  --report C:\Audio\GT\work\neural_qc.json
```

Если файлы модели имеют несовпадающую частоту, задержку или число кадров, модуль откажет в обработке: нельзя просто поменять метаданные частоты, нужна отдельная коррекция с контролем лагов. При плохой сумме и чрезмерной дельте он также откажет.

```powershell
python tools/mastering/neural_drumsep_bridge.py mix `
  --baseline-unlimited C:\Audio\GT\work\v21_raw_float32.wav `
  --delta C:\Audio\GT\work\drum_neural_delta_float32.wav `
  --output C:\Audio\GT\work\v24_unlimited_float32.wav
```

`v21_raw_float32.wav` — **неотлимитированный** baseline на 44.1 kHz; не подставлять готовый FLAC v2.3. Результат `mix` — ещё НЕ мастер: затем нужен float32-премастер −6 dBFS, финальный лимитер Astra, контроль LUFS/TP/LRA, mono fold-down, A/B на одинаковой громкости и FLAC24/16.

## Безопасные допуски на первом эксперименте

| Выходная нейросетевая дорожка | Начальное изменение |
|---|---:|
| Kick | +0.32 dB |
| Snare/Clap | −0.28 dB |
| Toms | 0 dB |
| Hi-hat | +0.48 dB |
| Cymbals | +0.10 dB |

- Непроверенная нейросетевая сумма сравнивается с оригинальным drums-стемом. Если relative reconstruction error хуже −15 dB, нужен review.
- Итоговая RMS-дельта должна быть менее −20 dB относительно исходного drums-стема (в противном случае processing stop).
- Полная сумма оригинальных ударных не подменяется нейросетевыми дорожками: меняется только `sum((gain−1) × selected_stem)`.
- Бас/гитара/пэды и одобренный Golden Teeth Studio Rework остаются неизменными.
- Положительный тест реконструкции на синтетических данных **не доказывает** чистого инструментального разделения на Golden Teeth.

## Проверка

```bash
python -m unittest discover -s tests -p 'test_neural_drumsep_bridge.py' -v
```

**12/12 локальных тестов PASS:** отказ при плохой реконструкции, отсутствии стемов, ошибке sample grid, опасных коэффициентах и попытке перезаписи; сохранение SHA-256, детерминизм, корректная сборка команд.

Инженерная приёмка после реального прогона: source SHA-256, checkpoint SHA-256, dropouts/артефакты (kick/snare/HH), sample time, phase/mono, true peak, A/B vs v2.3 и Studio Rework на одинаковой громкости. Никаких автоматических замен эталонных мастеров.