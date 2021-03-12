import logging.config
from os import environ
from argparse import ArgumentParser, FileType
from configparser import ConfigParser

import pika
from dotenv import load_dotenv

def _load_config() -> ConfigParser:
    parser = ArgumentParser(
        description="Backend NMT server for Sockeye models."
    )

    parser.add_argument('--config-file', type=FileType('r'), default='config/config.ini', help="Path to config file.")
    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config_file.name)
    return config

def _parse_factors():
    factors = eval(_config['factors']['factors'])
    sequence = eval(_config['factors']['sequence'])
    alt_factors = eval(_config['factors']['alt_factors'])

    factors = {factor:factors.setdefault(factor, ['{}0'.format(factor)]) for factor in sequence}
    parsed_factors = {}
    for k, v in factors.items():
        if v:
            _tmp = {"factors": v}
            if len(v) == 1:
                _tmp["used"] = False
            parsed_factors[k] = _tmp

    parsed_factors["sequence"] = sequence

    for factor in sequence:
        parsed_factors[factor]['mapping'] = {**alt_factors.setdefault(factor, {}),
                                             **{v:v for v in parsed_factors[factor]['factors']}}
    return parsed_factors


_config = _load_config()
logging.config.fileConfig('config/logging.conf', defaults={'logfile': _config['general']['logfile']})

load_dotenv("config/.env")

CPU = eval(_config['general']['cpu'])
CHAR_LIMIT = eval(_config['general']['char_limit'])

MQ_PARAMS = pika.ConnectionParameters \
    (host=environ.get('MQ_HOST'), port=environ.get('MQ_PORT'),
     credentials=pika.credentials.PlainCredentials(username=environ.get('MQ_USERNAME'),
                                                   password=environ.get('MQ_PASSWORD')))

MQ_EXCHANGE = _config['rabbitmq']['exchange']
MQ_QUEUE_NAME = _config['rabbitmq']['queue_name']
MQ_ALT_ROUTES = eval(_config['rabbitmq']['alt_routes'])

NMT_MODEL = _config['models']['nmt']
SPM_MODEL = _config['models']['spm']
TC_MODEL = _config['models']['tc']

FACTORS = _parse_factors()