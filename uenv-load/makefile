WRAPPER = uenv run prgenv-gnu/24.11:v2 --view=default --

CXX = $(WRAPPER) mpicxx

all: mpiinit.exe

mpiinit.exe: mpiinit.cpp
	$(CXX) mpiinit.cpp -o $@

clean:
	rm -f *.exe
