package com.football.livescore.controller;

import com.football.livescore.model.LiveScore;
import com.football.livescore.repository.LiveScoreRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

@RestController
@RequestMapping("/api/live-scores")
@RequiredArgsConstructor
public class LiveScoreController {

    private final LiveScoreRepository liveScoreRepository;
    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    @GetMapping(path = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamLiveScores() {
        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);
        this.emitters.add(emitter);

        emitter.onCompletion(() -> this.emitters.remove(emitter));
        emitter.onTimeout(() -> this.emitters.remove(emitter));
        emitter.onError((e) -> this.emitters.remove(emitter));

        // Immediately send initial data directly upon connection
        sendLatestScoresToEmitter(emitter);

        return emitter;
    }

    // Poll the database every 10 seconds and push to connected clients
    @Scheduled(fixedRate = 10000)
    public void pushLiveScores() {
        if (emitters.isEmpty()) return;

        List<LiveScore> latestScores = liveScoreRepository.findAll();
        if (latestScores.isEmpty()) return;

        for (SseEmitter emitter : emitters) {
            try {
                for(LiveScore score : latestScores) {
                    emitter.send(SseEmitter.event().name("live-score-update").data(score));
                }
            } catch (IOException e) {
                emitters.remove(emitter);
            }
        }
    }

    // Helper to send data to a single new client
    private void sendLatestScoresToEmitter(SseEmitter emitter) {
        List<LiveScore> latestScores = liveScoreRepository.findAll();
        try {
            for(LiveScore score : latestScores) {
                emitter.send(SseEmitter.event().name("live-score-update").data(score));
            }
        } catch (IOException e) {
            emitters.remove(emitter);
        }
    }
}
