def datetime_from_filename_string(date_str):
    from datetime import datetime
    return datetime.strptime(date_str, '%Y-%m-%dT%H-%M-%S')

def datetime_str(date):
    from datetime import datetime
    return date.strftime('%Y-%m-%dT%H:%M:%S')

def datetime_from_str(date_str):
    from datetime import datetime
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

def iter_time_buckets(start_datetime, duration_ms, step_ms):
    from datetime import datetime, timedelta

    abs_end = start_datetime + timedelta(milliseconds=duration_ms)
    step_delta = timedelta(milliseconds=step_ms)
    
    start = start_datetime
    end = start + step_delta
    while end <= abs_end:
        yield (start, end)
        start = end
        end += step_delta
    
    # not yielding final bucket unless the division is perfect
    # this is so there are exactly as many time buckets here as we get from the stats method
    # todo: consider having stats generate a final bucket so we can do the right thing here
    # (and thus change <= to just < above).
    #yield (start, abs_end)