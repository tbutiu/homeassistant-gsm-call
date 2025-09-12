# Contributing

Thank you for your interest in developing the GSM Call integration for Home Assistant!

If you'd like to suggest fixes or new features, here are a few guidelines.

## Discussing Changes

Before starting work on major changes or new features, **please discuss them first**:
1. **Search open [issues](https://github.com/black-roland/homeassistant-gsm-call/issues)** — your idea or issue might already be under discussion.
2. **Create a [discussion](https://github.com/black-roland/homeassistant-gsm-call/discussions) or [issue](https://github.com/black-roland/homeassistant-gsm-call/issues)** and describe what you want to implement or change. This helps avoid situations where you do work that I cannot accept for various reasons.

## Reporting Bugs and Feature Requests

If you found a bug or have an idea for a new feature — create an [issue](https://github.com/black-roland/homeassistant-gsm-call/issues). Before creating one, check if there's already an issue with a similar topic.

The more detailed your problem or suggestion description is (with reproduction steps, logs, HA versions), the faster I can respond.

## Adding Support for New Modems

PRs adding support for new modem models are very welcome!

If you can't implement a PR yourself (e.g., if you're not a programmer), you can still help by providing information about the required AT commands for your specific modem:

- Look for the necessary AT commands in your modem's documentation
- Alternatively, try to capture a log of the interaction between vendor software and your modem
- **Important**: Before creating feature requests, please test that these AT commands actually work by testing them through minicom, Putty, or other terminal software

This information is extremely valuable for implementing support.

## Pull Requests

PRs with fixes and improvements are always welcome! The process is simple:

1. Make sure your PR solves a specific problem or adds one clear feature.
2. Describe in the PR what exactly it changes and why.
3. Be prepared that I might ask for changes or clarifications.

Thank you for your contribution!

---

# Участие в разработке

Спасибо, что интересуетесь разработкой интеграции GSM Call для Home Assistant!

Если вы хотите предложить исправления или новые функции, вот несколько рекомендаций.

## Обсуждение изменений

Перед тем как начать работу над крупными изменениями или новыми функциями, **пожалуйста, сначала обсудите их**:
1. **Поищите открытые [issues](https://github.com/black-roland/homeassistant-gsm-call/issues)** — возможно, ваша идея или проблема уже обсуждается.
2. **Создайте [discussion](https://github.com/black-roland/homeassistant-gsm-call/discussions) или [issue](https://github.com/black-roland/homeassistant-gsm-call/issues)** и опишите, что вы хотите сделать или изменить. Это поможет избежать ситуации, когда вы делаете работу, которую я не смогу принять по каким-либо причинам.

## Сообщение об ошибках и запросы функций

Если вы нашли ошибку или у вас есть идея для новой функции — создайте [issue](https://github.com/black-roland/homeassistant-gsm-call/issues). Перед созданием проверьте, нет ли уже Issue с похожей темой.

Чем детальнее вы опишете проблему или предложение (с шагами для воспроизведения, логами, версиями HA), тем быстрее я смогу отреагировать.

## Добавление поддержки новых модемов

PR с добавлением поддержки новых моделей модемов очень приветствуются!

Если вы не можете реализовать PR самостоятельно (например, не умеете программировать), вы всё равно можете помочь, предоставив информацию о необходимых AT-командах для вашего конкретного модема:

- Поищите нужные AT-команды в документации к вашему модему.
- Или попытайтесь снять лог взаимодействия вендорного софта с модемом.
- **Важно**: Перед созданием feature requests, пожалуйста, проверьте, что эти AT-команды действительно работают — потестируйте через minicom, Putty или другой терминальный софт.

Эта информация чрезвычайно ценна для реализации поддержки.

## Pull Request'ы

PR с исправлениями и улучшениями всегда приветствуются! Процесс прост:

1. Убедитесь, что ваш PR решает конкретную проблему или добавляет одну чёткую функцию.
2. Опишите в PR, что именно он меняет и зачем.
3. Будьте готовы к тому, что я могу попросить внести правки.

Спасибо за ваш вклад!
