
nohup redis-server > ./log_data/redis-server.log &

nohup python logging_engine.py > ./log_data/logging_engine.log &

nohup python game_engine.py > ./log_data/game_renderer.log &

nohup gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app > ./log_data/gunicorn.log &