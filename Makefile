# Reflecto Developer Makefile

.PHONY: dev start stop rebuild logs cleanup

dev: start

start:
	./run_reflecto.sh start

stop:
	./run_reflecto.sh stop

rebuild:
	./run_reflecto.sh rebuild

logs:
	./run_reflecto.sh logs

cleanup:
	./run_reflecto.sh cleanup
