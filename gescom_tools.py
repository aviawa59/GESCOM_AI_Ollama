from database_tool import query_database


def get_meter_count():
    sql = """
        Select Count(*) as total_meter_installed
        from meter_mains
    """

    return query_database(sql)


def get_division_summary():
    sql = """
        Select
            cd.division,
            count(mm.account_id) as total_meter_installed
            from meter_mains mm
            left join consumer_details cd on mm.account_id = cd.account_id
            group by cd.division
    """
    return query_database(sql)


def get_division_meter_count(division_code):
    sql = """
        Select
            cd.division,
            count(mm.account_id) as total_meter_installed
            from meter_mains mm
            left join consumer_details cd on mm.account_id = cd.account_id
            where cd.division = :division_code
            group by cd.division
    """
    return query_database(sql, {"division_code": division_code})