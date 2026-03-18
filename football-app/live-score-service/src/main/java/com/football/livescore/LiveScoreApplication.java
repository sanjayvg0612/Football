package com.football.livescore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class LiveScoreApplication {

    public static void main(String[] args) {
        SpringApplication.run(LiveScoreApplication.class, args);
    }
}
