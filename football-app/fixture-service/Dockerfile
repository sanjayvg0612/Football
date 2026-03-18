FROM eclipse-temurin:17-jre-alpine

WORKDIR /app

COPY target/fixture-service-0.0.1-SNAPSHOT.jar /app/fixture-service.jar

EXPOSE 8082

CMD ["java", "-jar", "fixture-service.jar"]