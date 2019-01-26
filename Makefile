.PHONY: export-games build-stockfish-connect stockfishtcp

build-stockfishtcp:
	docker build -t stockfishtcp:dev -f Dockerfile.stockfishtcp .

run-stockfishtcp: build-stockfishtcp
	docker run --rm -p 3333:3333 stockfishtcp:dev /bin/stockfishtcp

export-games:
	@# See https://lichess.org/api#operation/gamesExportIds
	time curl "https://lichess.org/api/games/user/evanrthomas?clocks=true&evals=true&opening=true" > games.pgn
