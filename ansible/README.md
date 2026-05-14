# Ansible playbooks cho Windows SQL Server

Bộ playbook này dùng một môi trường duy nhất: Ubuntu control node quản lý các Windows managed nodes chạy Microsoft SQL Server qua WinRM.

## Cấu trúc

- `inventory.ini`: danh sách Windows SQL Server cần quản lý.
- `requirements.yml`: collection Ansible cần cài trên Ubuntu control node.
- `group_vars/windows_sql.yml`: biến cấu hình chung cho tất cả managed nodes.
- `deploy_python.yml`: triển khai `db_scan.py`, package `scanner/` và `requirements.txt` lên nhiều Windows server.
- `run_audit.yml`: chạy audit hàng loạt và ghi báo cáo JSON trên từng managed node.
- `remediate_sql_config.yml`: tắt/bật một cấu hình SQL Server bằng `sp_configure`.
- `collect_reports.yml`: thu thập các báo cáo JSON về Ubuntu control node trong `ansible/reports/`.
- `site.yml`: chạy lần lượt deploy, audit và collect report.

## Chuẩn bị nhanh

1. Cài collection cần thiết trên Ubuntu control node:

   ```bash
   ansible-galaxy collection install -r requirements.yml
   ```

2. Bật WinRM trên Windows managed nodes và bảo đảm tài khoản trong `inventory.ini` có quyền chạy PowerShell từ xa.
3. Bảo đảm Windows managed nodes đã có Python, `pip`, ODBC Driver 17 for SQL Server, module Python `pyodbc` có thể cài bằng pip và công cụ `sqlcmd` nếu cần remediation.
4. Sửa `inventory.ini` để thêm host thật và thay `ansible_user`/`ansible_password`.
5. Sửa `group_vars/windows_sql.yml` nếu SQL instance không phải `localhost\SQLEXPRESS01`.

## Cách chạy

Triển khai scanner lên tất cả server:

```bash
ansible-playbook -i inventory.ini deploy_python.yml
```

Chạy audit hàng loạt:

```bash
ansible-playbook -i inventory.ini run_audit.yml
```

Thu thập báo cáo về control node:

```bash
ansible-playbook -i inventory.ini collect_reports.yml
```

Chạy trọn luồng deploy + audit + collect:

```bash
ansible-playbook -i inventory.ini site.yml
```

Tắt một cấu hình SQL Server, ví dụ `xp_cmdshell = 0`:

```bash
ansible-playbook -i inventory.ini remediate_sql_config.yml \
  -e "sql_remediation_config_name=xp_cmdshell sql_remediation_config_value=0"
```

Bật lại cấu hình, ví dụ `xp_cmdshell = 1`:

```bash
ansible-playbook -i inventory.ini remediate_sql_config.yml \
  -e "sql_remediation_config_name=xp_cmdshell sql_remediation_config_value=1"
```
