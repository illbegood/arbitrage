def routine(path):
    rates = get_rates(path)
    volume = get_volume('USDT')
    volumes = []
    for rate in rates:
        volume = truncate(volume)
        volumes.append(volume)
        volume *= rate
    trade(volumes, path)    

