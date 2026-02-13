CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -I../../../c

all: main

main: main.c
	$(CC) $(CFLAGS) -c main.c -o main.o
	@echo "Syntax check passed (linking requires zpe-iot static lib)"

clean:
	rm -f main.o
