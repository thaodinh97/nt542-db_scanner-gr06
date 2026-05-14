import json
import os

import pyodbc

from scanner import (
    scan_auth_and_authz,
    scan_auditing_logging,
    scan_encryption,
    scan_password_policies,
    scan_surface_area,
    scan_application_development,
)


# ==============================================================================
# HAM MAIN: KET NOI VA GOI CAC MODULES
# ==============================================================================
def build_connection_string():
    """Build SQL Server ODBC connection string from environment variables."""
    explicit_conn_str = os.getenv("DB_SCANNER_CONN_STR")
    if explicit_conn_str:
        return explicit_conn_str

    driver = os.getenv("DB_SCANNER_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
    server = os.getenv("DB_SCANNER_SQL_INSTANCE", r"localhost\SQLEXPRESS01")
    database = os.getenv("DB_SCANNER_SQL_DATABASE", "master")
    trusted_connection = os.getenv("DB_SCANNER_TRUSTED_CONNECTION", "yes")
    encrypt = os.getenv("DB_SCANNER_ENCRYPT", "yes")
    trust_server_certificate = os.getenv("DB_SCANNER_TRUST_SERVER_CERTIFICATE", "yes")
    timeout = os.getenv("DB_SCANNER_TIMEOUT", "0")

    return (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection={trusted_connection};"
        f"Encrypt={encrypt};"
        f"TrustServerCertificate={trust_server_certificate};"
        f"Timeout={timeout};"
    )


def run_full_automated_scan():
    conn_str = build_connection_string()

    final_report = []

    try:
        # Thực hiện kết nối
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Gọi tuần tự từng module (Đảm bảo bạn đã có các hàm scan này ở trên)
        final_report.extend(scan_surface_area(cursor))
        final_report.extend(scan_auth_and_authz(cursor))
        final_report.extend(scan_application_development(cursor))
        # Nếu bạn đã viết các module khác (password, audit, encryption) thì gỡ comment ở dưới
        final_report.extend(scan_password_policies(cursor))
        final_report.extend(scan_auditing_logging(cursor))
        final_report.extend(scan_encryption(cursor))


        conn.close()

    except Exception as e:
        final_report.append({
            "status": "Error",
            "details": f"Không thể kết nối đến Database: {e}"
        })

    # Xuất kết quả phân tích
    print(json.dumps(final_report, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    run_full_automated_scan()
