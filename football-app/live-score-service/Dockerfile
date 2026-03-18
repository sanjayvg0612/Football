FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY target/live-score-service-0.0.1-SNAPSHOT.jar /app/live-score-service.jar

EXPOSE 8081

CMD ["java", "-jar", "live-score-service.jar"]
