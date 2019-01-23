.PHONY: build-stockfish-connect stockfishtcp

build-stockfishtcp:
	docker build -t stockfishtcp:dev -f Dockerfile.stockfishtcp .

stockfishtcp: build-stockfishtcp
	docker run --rm -p 3333:3333 stockfishtcp:dev /bin/stockfishtcp
