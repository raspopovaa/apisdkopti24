---
description: "Учебные примеры: Отчёты"
---

# Отчёты

Заказ отчётов по договору и картам, список заказанных отчётов и скачивание готовых файлов.

| Пример | HTTP | Изменяет данные | Тарифицируется | DEMO |
|---|---|:---:|:---:|:---:|
| [Доступные отчёты](get_reports.md) | GET `reports` | Нет | Нет | Да |
| [Заказ отчёта](order_report.md) | POST `reports` | Да | Да | Да |
| [Заказанные отчёты](get_report_jobs.md) | GET `reports/jobs` | Нет | Нет | Да |
| [Скачивание файла отчёта](download_report_file.md) | GET `reports/jobs/{job_id}` | Нет | Да | Нет |
| [Заказ транзакционного отчёта (API v1)](order_report_v1.md) | GET `reports` | Да | Да | Нет |
| [Заказанные отчёты (API v1)](get_report_job_list_v1.md) | GET `getReportJobList` | Нет | Нет | Да |
| [Скачивание файла отчёта (API v1)](download_report_file_v1.md) | GET `getReportFile` | Нет | Да | Нет |
