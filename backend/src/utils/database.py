# SUPABASE HELPER FUNCTIONS
from typing import Any
from core.supabase_client import supabase

class SupabaseDatabaseHelper:
    """Helper class for common Supabase database operations."""

    @staticmethod
    def insert_records(
        table_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
    ):
        """
        Insert one or more records into a table.
        SQL Equivalent:
            INSERT INTO table_name (...);
        """
        if not records:
            return None
        return (
            supabase
            .table(table_name)
            .insert(records)
            .execute()
        )

    @staticmethod
    def upsert_records(
        table_name: str,
        records: dict[str, Any] | list[dict[str, Any]],
        on_conflict: str,
    ):
        """
        Insert or update records when a conflict occurs.
        SQL Equivalent:
            INSERT ...
            ON CONFLICT (...)
            DO UPDATE;
        """
        if not records:
            return None
        return (
            supabase
            .table(table_name)
            .upsert(
                records,
                on_conflict=on_conflict,
            )
            .execute()
        )

    @staticmethod
    def get_records(
        table_name: str,
    ):
        """
        Retrieve all records from a table.
        SQL Equivalent:
            SELECT *
            FROM table_name;
        """
        return (
            supabase
            .table(table_name)
            .select("*")
            .execute()
        )

    @staticmethod
    def get_record_by_id(
        table_name: str,
        column_name: str,
        value: Any,
    ):
        """
        Retrieve a single record by an identifier.
        SQL Equivalent:
            SELECT *
            FROM table_name
            WHERE column_name = value;
        """
        return (
            supabase
            .table(table_name)
            .select("*")
            .eq(column_name, value)
            .limit(1)
            .execute()
        )

    @staticmethod
    def get_records_by_column(
        table_name: str,
        column_name: str,
        value: Any,
    ):
        """
        Retrieve records matching a value.
        SQL Equivalent:
            SELECT *
            FROM table_name
            WHERE column_name = value;
        """
        return (
            supabase
            .table(table_name)
            .select("*")
            .eq(column_name, value)
            .execute()
        )

    @staticmethod
    def get_records_in(
        table_name: str,
        column_name: str,
        values: list[Any],
    ):
        """
        Retrieve records where a column exists in a list.
        SQL Equivalent:
            SELECT *
            FROM table_name
            WHERE column_name IN (...);
        """
        return (
            supabase
            .table(table_name)
            .select("*")
            .in_(column_name, values)
            .execute()
        )

    @staticmethod
    def update_records(
        table_name: str,
        column_name: str,
        value: Any,
        update_data: dict[str, Any],
    ):
        """
        Update records matching a condition.
        SQL Equivalent:
            UPDATE table_name
            SET ...
            WHERE column_name = value;
        """
        return (
            supabase
            .table(table_name)
            .update(update_data)
            .eq(column_name, value)
            .execute()
        )

    @staticmethod
    def delete_records(
        table_name: str,
        column_name: str,
        value: Any,
    ):
        """
        Delete records matching a condition.
        SQL Equivalent:
            DELETE
            FROM table_name
            WHERE column_name = value;
        """
        return (
            supabase
            .table(table_name)
            .delete()
            .eq(column_name, value)
            .execute()
        )

    @staticmethod
    def count_records(
        table_name: str,
    ):
        """
        Count all records in a table.
        SQL Equivalent:
            SELECT COUNT(*)
            FROM table_name;
        """
        return (
            supabase
            .table(table_name)
            .select("*", count="exact")
            .execute()
        )

    @staticmethod
    def count_records_by_column(
        table_name: str,
        column_name: str,
        value: Any,
    ):
        """
        Count records matching a value.
        SQL Equivalent:
            SELECT COUNT(*)
            FROM table_name
            WHERE column_name = value;
        """
        return (
            supabase
            .table(table_name)
            .select("*", count="exact")
            .eq(column_name, value)
            .execute()
        )

    @staticmethod
    def get_records_select(
        table_name: str,
        columns: str,
    ):
        """
        Retrieve specific columns.
        SQL Equivalent:
            SELECT col1, col2
            FROM table_name;
        """
        return (
            supabase
            .table(table_name)
            .select(columns)
            .execute()
        )