WRAPPER = uenv run prgenv-gnu/25.11:v1 --view=default --

CXX = $(WRAPPER) mpicxx

all: mpiinit.exe

mpiinit.exe: mpiinit.cpp
	$(CXX) mpiinit.cpp -o $@

clean:
	rm -f *.exe
