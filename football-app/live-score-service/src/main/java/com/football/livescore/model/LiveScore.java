package com.football.livescore.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

@Entity
@Table(name = "live_scores")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LiveScore {

    @Id
    private Long matchId;

    private String homeTeam;
    private String awayTeam;
    private Integer homeScore;
    private Integer awayScore;
    private String minute;
    private String status;
    private LocalDateTime updatedAt;
}
