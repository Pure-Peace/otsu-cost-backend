gcc -Wall -g  -fPIC -c cost_linux.cpp -o cost.o
gcc -shared cost.o -o cost.so