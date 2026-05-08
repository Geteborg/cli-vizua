<div align="center">

```
 ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ 
 ██║   ██║██║╚══███╔╝██║   ██║██╔══██╗
 ██║   ██║██║  ███╔╝ ██║   ██║███████║
 ╚██╗ ██╔╝██║ ███╔╝  ██║   ██║██╔══██║
  ╚████╔╝ ██║███████╗╚██████╔╝██║  ██║
   ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
```

**CLI-инструмент для автоматической визуализации данных на основе ИИ**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Typer](https://img.shields.io/badge/CLI-Typer-009688?style=flat-square)](https://typer.tiangolo.com)
[![Pandas](https://img.shields.io/badge/Data-Pandas-150458?style=flat-square&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/status-в%20разработке-orange?style=flat-square)]()

</div>

---

## 💡 Зачем это нужно?

Изучая аналитику данных, я постоянно сталкивался с одной проблемой: **как правильно визуализировать данные?** Какой тип графика выбрать? Как расставить акценты? Что вообще стоит показать?

**vizua** — это инструмент, который отвечает на эти вопросы автоматически. Передайте ему датасет — он проанализирует структуру, выявит закономерности и предложит (или сразу построит) подходящие визуализации.

---

## ✨ Возможности

- 📊 **Автоматическое профилирование** — анализ типов данных, распределений, пропусков и выбросов
- 🤖 **ИИ-рекомендации** — умный подбор типа графика под каждую переменную и задачу
- ⚡ **CLI-интерфейс** — быстрый запуск из терминала без лишнего кода
- 📁 **Поддержка CSV** — работа с табличными данными через pandas
- 🔌 **Расширяемость** — архитектура позволяет подключить OpenAI API и внешние BI-инструменты

---

## 🚀 Быстрый старт

### Установка

```bash
# Клонируй репозиторий
git clone https://github.com/Geteborg/cli-vizua.git
cd cli-vizua

# Установи зависимости
pip install -e .
```

### Использование

```bash
# Профилирование датасета
vizua profile data.csv

# Получить рекомендации по визуализации
vizua recommend data.csv

# Автоматически построить графики
vizua visualize data.csv --output ./charts
```

---

## 🗂 Структура проекта

```
cli-vizua/
├── src/
│   └── vizua/          # Основной пакет
├── pyproject.toml      # Конфигурация проекта
├── .gitignore
└── README.md
```

---

## 🛠 Стек технологий

| Компонент | Технология |
|-----------|------------|
| CLI-фреймворк | [Typer](https://typer.tiangolo.com) |
| Работа с данными | [Pandas](https://pandas.pydata.org) |
| ИИ-рекомендации | OpenAI API *(в разработке)* |
| Язык | Python 3.11+ |

---

## 🗺 Roadmap

- [x] Базовая структура CLI-инструмента
- [x] Профилирование данных через pandas
- [x] Автоматическая генерация графиков (matplotlib / plotly)
- [x] Экспорт в HTML-отчёт
- [ ] Web-интерфейс
- [ ] Интеграция с OpenAI API для анализа и рекомендаций
- [ ] Интеграция с Tableau / Yandex DataLens

---

## 🤝 Участие в разработке

Проект находится на ранней стадии, и любой вклад приветствуется!

1. Fork репозитория
2. Создай ветку (`git checkout -b feature/my-feature`)
3. Закоммить изменения (`git commit -m 'Add my feature'`)
4. Push в ветку (`git push origin feature/my-feature`)
5. Открой Pull Request

---

## 👨‍💻 Автор

Сделано студентом-аналитиком данных, который устал вручную подбирать типы графиков.

---

<div align="center">
<sub>⭐ Если проект оказался полезным — поставь звезду на GitHub!</sub>
</div>
