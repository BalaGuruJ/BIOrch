class Identity:
    @staticmethod
    def table_id(table_name: str) -> str:
        return f"table:{table_name}"

    @staticmethod
    def column_id(table_id: str, column_name: str) -> str:
        return f"{table_id}:{column_name}"

    @staticmethod
    def measure_id(table_id: str, measure_name: str) -> str:
        return f"{table_id}:{measure_name}"

    @staticmethod
    def relationship_id(from_table_id: str, from_column_id: str, to_table_id: str, to_column_id: str, index: int = 0) -> str:
        base = f"rel:{from_table_id}:{from_column_id}:{to_table_id}:{to_column_id}"
        if index > 0:
            return f"{base}:{index}"
        return base
