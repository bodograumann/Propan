---
hide:
  - toc
---

# Документирование

**Propan** позволяет вам не думать о документации своего проекта - она уже сгенерирована автоматически в соответсвии со спецификацией [**AsyncAPI**]({{ urls.asyncapi }}){.external-link target="_blank"}!

## Пример

Давайте разберемся на примере, как это работает.

Для начала напишем небольшое приложение примерно следующего содержания:

```python linenums='1'
{!> docs_src/quickstart/documentation/example.py !}
```

## YAML схема

Для того, чтобы сгенерировать **AsyncAPI** спецификацию вашего проекта в формате `.yaml` используйте следующую команду:

<div class="termy">
```console
$ propan docs gen example:app

Your project AsyncAPI scheme was placed to `./asyncapi.yaml`
```
</div>

Теперь у вас есть схема вашего проекта: вы можете использовать ее для генерации различных клиентов на любом языке с помощью соответсвующих инструментов [**AsyncAPI**]({{ urls.asyncapi }}/tools/generator){.external-link target="_blank"}

???- example "Asyncapi.yaml"
    ```yaml
    {!> docs_src/quickstart/documentation/example.yaml !}
    ```

## Онлайн документация

Также, **Propan** позволяет вам развернуть HTML-представление вашей документации следующей командой

!!! warning ""
    Онлайн представлени документации не работает без интернет-соединения, так как для ее отображения используются **CDN** зависимости.

<div class="termy">
```console
$ propan docs serve example:app
```
</div>

Так вы можете предоставить всем внешним потребителям доступ к документации вашего проекта без дополнительных затрат на разработку.

???- example "HTML page"
    ![HTML-page](../../assets/img/docs-html.png)

!!! tip
    **Propan** также можете хостить `asyncapi.yaml` файлы.

    ```console
    propan docs serve asyncapi.yaml
    ```
    Это может быть полезно если вы хотите расширить автоматически сгенерированную **AsyncAPI** документацию: вы просто генерирует файл, дорабатываете его и хостите!

При использовании онлайн документации вы также можете скачать ее по соответствующим путям:

* `/asyncapi.json` - **JSON** схема (доступно при хостинге приложения)
* `/asyncapi.yaml` - **YAML** схема (доступна как для приложения, так и для файла)

### FastAPI Plugin

При использовании **Propan** в качестве роутера для **FastAPI**, фреймворк автоматически регистрирует эндпоинты для хостинга **AsyncAPI** документации в ваше приложение со следующими значениями по умолчанию:

```python linenums='1'
{!> docs_src/quickstart/documentation/fastapi.py !}
```

## Собственный хостинг

Для хостинга документации онлайн **Propan** использует **FastAPI** + **uvicorn**.
Возможно, вы захотите самостоятельно реализовать логику показа документации: ограничить права доступа, кастомизировать контент в заивисмоти от прав доступа, встроить документацию в свое frontend-приложение и тд.
Для это вы можете самостоятельно сгенерировать `json`/`yaml`/`html` документ и использовать в собственном сервисе.

```python linenums='1' hl_lines="9-12"
{!> docs_src/quickstart/documentation/custom_schema.py !}
```