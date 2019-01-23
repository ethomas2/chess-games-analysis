package main

import (
	"bufio"
	"fmt"
	"io"
	"net"
	"os"
	"os/exec"
)

const (
	CONN_HOST = "localhost"
	CONN_PORT = "3333"
	CONN_TYPE = "tcp"
)

func main() {
	l, err := net.Listen("tcp", "0.0.0.0:3333")
	if err != nil {
		fmt.Println("Error listening:", err.Error())
		os.Exit(1)
	}
	fmt.Println("Listening ...")
	defer l.Close()
	// Listen for an incoming connection.
	conn, err := l.Accept()
	fmt.Println("Accepted")
	if err != nil {
		fmt.Println("Error accepting: ", err.Error())
		os.Exit(1)
	}

	cmd := exec.Command("stockfishtcp")
	cmd.Stdin = conn
	cmd.Stdout = conn
	err = cmd.Run()
	if err != nil {
		fmt.Printf("\033[31m%s\033[m\n", err)
	}

}

func echoTCP(conn net.Conn) {
	for {
		reader := bufio.NewReader(conn)
		line, err := reader.ReadString('\n')
		fmt.Fprintln(conn, line)
		if err == io.EOF {
			break
		} else if err != nil {
			fmt.Printf("\033[31m%s\033[m\n", err)
		}
	}
}

func discard1() {
	// wg := sync.WaitGroup{}
	// wg.Add(2)
	// go func() {
	// 	_, err := io.Copy(stockfishin, conn)
	// 	if err != nil {
	// 		fmt.Printf("\033[31m%s\033[m\n", err)
	// 	}
	// 	wg.Done()
	// }()
	// go func() {
	// 	_, err := io.Copy(stockfishout, conn)
	// 	if err != nil {
	// 		fmt.Printf("\033[31m%s\033[m\n", err)
	// 	}
	// 	wg.Done()
	// }()
}
