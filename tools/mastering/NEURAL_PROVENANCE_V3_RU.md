# TREBLO / Astra Audio v3.0 — Neural Kick Provenance Gate

**Результат:** добавлен контроль подлинности входных аудиоданных перед мастерингом Neural Kick. Это **защитный релиз кода**, а не новый музыкальный мастер. Рендер v2.8 теперь рекомендуется запускать только через `neural_master_v30.py`.

## Что выявлено на настоящих файлах Golden Teeth

- `drums golden teeth.wav`: 44 100 Гц, стерео, 10 553 345 кадров, PCM16, SHA-256 `77b959343845fe07d6b17cf8a25ee27b3fb9dfb79f33d0fa939bc4c7dbffd3a7`.
- `GT_v23_UNLIMITED_RECOVERED_FLOAT32.wav`: та же сетка, float32, SHA-256 `656ec5cf219871d6aecbd1a5f49836d53640060a74e5d8bfc136955ce51c127f`.
- Реальный checkpoint MDX23C 6-stem **в локальной среде отсутствует**; прямой доступ к release assets невозможен (DNS/network). Настоящий CPU-инференс ранее был подтверждён в GitHub Actions **на синтетическом аудио**, но полный Golden Teeth через модель пока НЕ обрабатывался.

## Новые проверки перед Neural Kick Master

1. Наличие `INFERENCE_REPORT.json` из **официального адаптера v2.5**, `inference_performed=true`, правильные модель, движок, выходные имена, sample rate и число кадров.
2. SHA-256 именно `drums golden teeth.wav` и каждого из пяти predicted float32 WAV; проверка ожидаемых SHA-256 checkpoint/config. Без совпадения вход не принимается.
3. Проверка фактического аудиопотока: конечные значения, стерео, float32, совпадение кадров, recon error, оконные оценки и относительная задержка до ±1 кадра.
4. Отказ, если изменения противоречат ограничениям Astra, рабочая папка существует, отсутствует исходный unlimited float или неправильный параметр усиления kick.
5. Изменения ограничены kick +0...0.35 dB, с последующим объективным QC на экспортированном FLAC и обязательным A/B на слух. Snare, hats, toms, cymbals не переносятся в микс заново.

**Важно:** обычный JSON-отчёт и SHA файлов доказывают *целостность и согласованность* с данными адаптера, но не являются криптографической аттестацией факта выполнения обученной модели. Поэтому в QC явно фиксируется `cryptographic_model_execution_attestation=false`. Также численные проверки не гарантируют отсутствие bleed или субъективное улучшение.

## Использование — Windows / Python 3.11

Нужно локально иметь проверенные веса DrumSep (не распространяются вместе с кодом). 

```powershell
# Установка зависимостей из проверенной ревизии; FFmpeg должен быть в PATH
python -m pip install numpy scipy soundfile pedalboard
python -m pip install "mdxnet-infer @ git+https://github.com/openmirlab/mdxnet-infer.git@cb4779eedeca4f55ba498df8e234e2b5f4b90aaf"

# Проверка доступности входных данных и весов
python tools/mastering/neural_master_v30.py doctor `
  --drums "C:\Audio\drums golden teeth.wav" `
  --unlimited "C:\Audio\GT_v23_UNLIMITED_RECOVERED_FLOAT32.wav"

# Если веса загружены и проверены, запустить настоящий inference v2.5
python tools/mastering/drumsep_6stem_float_bridge.py `
  --input "C:\Audio\drums golden teeth.wav" `
  --output-dir "C:\Audio\inference" `
  --cache-dir "C:\Audio\models" `
  --device cpu

# Сначала проверка происхождения ВСЕХ результатов нейросети
python tools/mastering/neural_master_v30.py check `
  --drums "C:\Audio\drums golden teeth.wav" `
  --predicted "C:\Audio\inference\drums golden teeth"

# И только затем полный мастеринг из unlimited float, а не готового v2.3 FLAC
python tools/mastering/neural_master_v30.py render `
  --drums "C:\Audio\drums golden teeth.wav" `
  --unlimited "C:\Audio\GT_v23_UNLIMITED_RECOVERED_FLOAT32.wav" `
  --v23-master "C:\Audio\Golden_Teeth_Transient_Precision_v2_3_24bit.flac" `
  --studio-rework "C:\Audio\GT_Studio_Rework_MASTER.flac" `
  --predicted "C:\Audio\inference\drums golden teeth" `
  --workdir "C:\Audio\experiments\Neural_Kick_v3" `
  --kick-db 0.25
```

Запуск с `--allow-download` в адаптере v2.5 требует явного решения пользователя, потому что он скачивает ~438 МБ сторонних весов. **Не загружать приватные исходники на публичный GitHub**. Условия коммерческого использования весов DrumSep остаются не подтверждены — не развёртывать модель в платном сервисе до проверки прав.

## Тесты

```bash
PYTHONPATH=tools/mastering python -m unittest discover -s tests -p 'test_neural_*v30.py' -v
PYTHONPATH=tools/mastering python -m unittest discover -s tests -p 'test_neural_provenance_gate.py' -v
```

В локальной среде проверены 16 тестов (все PASS), включая сквозной рендер реальных FLAC24/16 через FFmpeg на синтетических нейропредсказаниях. Настоящая модель в этом наборе тестов не загружается; используются тестовые PCM и специально созданные манифесты.

## Следующие критерии качества

При появлении подлинных нейростемов Golden Teeth: проверить распознавание/перетекание kick в hh/snare, оценить phase/latency/reconstruction, `kick-only +0.10 / +0.25 / +0.35 dB`, посчитать true peak/LUFS/LRA, собрать A/B, где громкости выровнены. Сохранять v2.3 и одобренный Studio Rework нетронутыми до проверки слушателем.