def read_config(config):
    config = open(config, 'r')
    urls = list()

    line = config.readline().strip()
    while line:
        urls.append(line)
        line = config.readline().strip()

    return urls
