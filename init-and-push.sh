#!/usr/bin/env bash
# Инициализация репозитория и отправка на GitHub.
# Использование:  bash init-and-push.sh https://github.com/<логин>/<репозиторий>.git
set -euo pipefail
REMOTE="${1:?укажите адрес репозитория, например https://github.com/ivanov/fokus-prototype.git}"
cd "$(dirname "$0")"
if [ ! -d .git ]; then
  git init -q -b main
  git config user.name "${GIT_NAME:-FOKUS Project}"
  git config user.email "${GIT_EMAIL:-project@fokus.example}"
  git add -A
  git commit -q -m "Прототип информационного портала «ФОКУС»: 8 экранов, аналитический отчёт, бриф и передача проекта"
  echo "Репозиторий инициализирован, коммит создан."
fi
git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin main
echo
echo "Готово. Дальше включите Pages: Settings → Pages → Source = «GitHub Actions»."
echo "Сайт появится через 1–3 минуты: https://<логин>.github.io/<репозиторий>/"
