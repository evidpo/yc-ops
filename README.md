# yc-ops

CLI для управления ресурсами Yandex Cloud. Запуск, остановка и мониторинг виртуальных машин и управляемых баз данных одной командой.

Работает автономно и как инструмент для AI-агентов (Claude Code, Cursor и т.д.) через bash.

## Установка yc-ops

```bash
# через uv (рекомендуется)
uv tool install yc-ops

# или через pip
pip install yc-ops
```

---

## Подготовка с нуля

Если у вас ничего не настроено — начните отсюда. Если Yandex Cloud CLI уже установлен и настроен, переходите к разделу "Быстрый старт".

### Шаг 1. Создание аккаунта Yandex Cloud

1. Откройте https://console.yandex.cloud/
2. Нажмите "Подключиться" (или "Войти", если у вас есть Яндекс ID)
3. Войдите через Яндекс ID. Если его нет — создайте на https://passport.yandex.ru/
4. После входа вы попадёте в консоль управления

### Шаг 2. Платёжный аккаунт

Без платёжного аккаунта нельзя создавать ресурсы (даже бесплатные).

1. В консоли откройте "Billing" (левое меню, внизу) или перейдите на https://console.yandex.cloud/billing
2. Нажмите "Создать платёжный аккаунт"
3. Выберите тип: "Физическое лицо" или "Юридическое лицо"
4. Привяжите карту (для физлица) или укажите реквизиты (для юрлица)
5. Подтвердите создание

Новые аккаунты получают грант (стартовый баланс для тестирования). Деньги с карты не списываются, пока грант не закончится.

### Шаг 3. Облако и каталог

При первом входе Yandex Cloud автоматически создаёт:
- **Облако** (cloud) — верхний уровень, контейнер для всех ресурсов
- **Каталог** (folder) `default` — внутри облака, сюда складываются ресурсы

Можно работать с `default` или создать отдельный каталог:

1. В консоли: левое меню -> название облака -> "Создать каталог"
2. Укажите имя (например, `production` или `dev`)
3. Нажмите "Создать"

Запомните имя каталога — оно понадобится при настройке CLI.

### Шаг 4. Установка Yandex Cloud CLI

**macOS / Linux:**

```bash
curl -sSL https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash
```

После установки перезапустите терминал (или выполните `source ~/.bashrc` / `source ~/.zshrc`).

**Windows (PowerShell):**

```powershell
iex (New-Object System.Net.WebClient).DownloadString('https://storage.yandexcloud.net/yandexcloud-yc/install.ps1')
```

Проверьте, что CLI установился:

```bash
yc version
```

Должно вывести что-то вроде `Yandex Cloud CLI 0.XXX.0`.

### Шаг 5. Инициализация CLI

```bash
yc init
```

CLI задаст вопросы:

1. **OAuth-токен** — нажмите Enter, откроется браузер. Авторизуйтесь и скопируйте токен обратно в терминал
2. **Облако** — выберите из списка (если одно — подтвердите)
3. **Каталог** — выберите `default` или тот, который создали на шаге 3
4. **Зона доступности** — выберите `ru-central1-a` (или другую, если знаете какую)

Проверка:

```bash
yc config list
```

Должно показать `token`, `cloud-id`, `folder-id`, `compute-default-zone`.

### Шаг 6. Создание ресурсов (если их ещё нет)

yc-ops управляет уже существующими ресурсами. Если ресурсов нет, создайте их.

**Виртуальная машина:**

```bash
yc compute instance create \
  --name my-app-server \
  --zone ru-central1-a \
  --platform standard-v3 \
  --cores 2 --memory 4 --core-fraction 20 \
  --preemptible \
  --create-boot-disk image-folder-id=standard-images,image-family=ubuntu-2204-lts,size=30 \
  --network-interface subnet-name=default-ru-central1-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_rsa.pub
```

**Managed PostgreSQL:**

```bash
yc managed-postgresql cluster create \
  --name my-pg-cluster \
  --environment production \
  --network-name default \
  --host zone-id=ru-central1-a,subnet-name=default-ru-central1-a \
  --resource-preset s2.micro \
  --disk-size 10 \
  --disk-type network-ssd \
  --database name=mydb,owner=myuser \
  --user name=myuser,password=YOUR_PASSWORD
```

Эти команды для примера. Параметры (cores, memory, disk-size, preset) зависят от ваших задач.

---

## Быстрый старт

```bash
# Интерактивная настройка: указываете путь к yc и регистрируете ресурсы
yc-ops init

# Управление ресурсами
yc-ops start            # запустить все
yc-ops stop             # остановить все
yc-ops status           # таблица статусов
yc-ops start my-vm      # запустить конкретный ресурс
yc-ops stop my-pg       # остановить конкретный ресурс

# Конфигурация
yc-ops config           # показать текущий конфиг
yc-ops remove my-vm     # убрать ресурс из конфига
```

## Поддерживаемые типы ресурсов

| Тип | Что это |
|-----|---------|
| `compute` | Виртуальные машины, прерываемые инстансы |
| `managed-postgresql` | Управляемый PostgreSQL |
| `managed-mysql` | Управляемый MySQL |
| `managed-clickhouse` | Управляемый ClickHouse |
| `managed-redis` | Управляемый Redis |

## Конфигурация

yc-ops ищет конфиг в таком порядке:

1. `yc-ops.yaml` в текущей директории (per-repo конфиг)
2. `~/.config/yc-ops/config.yaml` (глобальный конфиг)

Если в корне репозитория лежит `yc-ops.yaml` — он используется автоматически. Это позволяет в разных проектах работать с разными ресурсами и облаками.

### Глобальный конфиг (один на все проекты)

```bash
yc-ops init
```

Сохраняется в `~/.config/yc-ops/config.yaml`.

### Per-repo конфиг (для конкретного проекта)

```bash
# Из корня вашего репозитория:
yc-ops init --local
```

Создаст `yc-ops.yaml` в текущей директории. Формат файла:

```yaml
yc_path: ~/.yandex-cloud/bin/yc
resources:
  - name: my-app-server
    type: compute
  - name: my-pg-cluster
    type: managed-postgresql
```

Можно создать этот файл вручную — формат тот же.

### Как это работает

```bash
cd ~/coding/project-a     # есть yc-ops.yaml с ресурсами project-a
yc-ops status              # показывает ресурсы project-a

cd ~/coding/project-b     # есть yc-ops.yaml с ресурсами project-b
yc-ops status              # показывает ресурсы project-b

cd ~/Desktop              # нет yc-ops.yaml
yc-ops status              # использует глобальный конфиг
```

`yc-ops config` всегда покажет, какой конфиг используется (local или global).

---

## Сервисный аккаунт (для серверов и CI)

На своём ноутбуке yc-ops работает с вашим личным токеном (который создался при `yc init`). На серверах и в CI нужен сервисный аккаунт.

### Создание сервисного аккаунта

```bash
# Создать аккаунт
yc iam service-account create --name yc-ops-sa

# Получить его ID
SA_ID=$(yc iam service-account get yc-ops-sa --format json \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['id'])")

# Выдать роль editor на каталог
FOLDER_ID=$(yc config get folder-id)
yc resource-manager folder add-access-binding $FOLDER_ID \
  --role editor \
  --subject serviceAccount:$SA_ID
```

### Создание авторизованного ключа

```bash
yc iam key create --service-account-name yc-ops-sa --output sa-key.json
```

Файл `sa-key.json` — это ваш ключ доступа. Храните его в безопасном месте. Не коммитьте в git.

### Настройка профиля для сервисного аккаунта

```bash
yc config profile create yc-ops-sa
yc config set service-account-key sa-key.json
yc config set folder-id $FOLDER_ID
```

Переключение между профилями:

```bash
yc config profile activate yc-ops-sa   # сервисный аккаунт
yc config profile activate default      # личный аккаунт
```

### Передача ключа на сервер

```bash
# Скопировать ключ на сервер
scp sa-key.json user@server:~/.config/yc-ops/sa-key.json

# На сервере: установить yc CLI и настроить профиль
yc config profile create yc-ops-sa
yc config set service-account-key ~/.config/yc-ops/sa-key.json
yc config set folder-id <YOUR_FOLDER_ID>
```

---

## Использование с AI-агентами

Любой агент, умеющий запускать bash-команды, может использовать yc-ops.

Пример инструкции для CLAUDE.md или системного промпта:

```
Для управления инфраструктурой используй yc-ops:
- `yc-ops status` — проверить состояние ресурсов
- `yc-ops start` — запустить перед деплоем
- `yc-ops stop` — остановить после работы для экономии
```

## Лицензия

MIT
