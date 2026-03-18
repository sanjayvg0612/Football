package com.football.livescore.repository;

import com.football.livescore.model.LiveScore;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface LiveScoreRepository extends JpaRepository<LiveScore, Long> {
    List<LiveScore> findByStatus(String status);
}
