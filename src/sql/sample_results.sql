-- Some initial games.
INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (1, "game1", "fs1", 1);
INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (2, "game1", "fs1", 2);

INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (3, "game2", "fs1", 1);
INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (4, "game2", "fs1", 2);

INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (5, "game3", "fs2", 1);
INSERT OR IGNORE INTO FlashGame (id, gameId, flashsetId, user) VALUES (6, "game3", "fs2", 2);

-- Point-is, user 1 has fc1 correct here, incorrect in game 2;
--                  and game3's fc1 is from a different fs, so isn't counted.

-- Some Flashcards played.
-- Win
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (0,  "game1", "fs1", "fc1", 1, "fc1");
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (1,  "game1", "fs1", "fc1", 2, "fc2");

-- Loss
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (2, "game2", "fs1", "fc2", 1, "fc3");
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (3, "game2", "fs1", "fc2", 2, "fc2");

-- Draw
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (4, "game3", "fs2", "fc1", 1, "fc1");
INSERT OR IGNORE INTO FlashCardInGame (id, gameId, flashsetId, flashcardId, user, userAns)
                               VALUES (5, "game3", "fs2", "fc1", 1, "fc1");

