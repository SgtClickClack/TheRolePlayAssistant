const request = require('supertest');
const express = require('express');
const feedbackRoutes = require('../feedbackRoutes');
const mongoose = require('mongoose');

const app = express();
app.use(express.json());
app.use('/api/feedback', feedbackRoutes);

describe('Feedback API', () => {
  beforeAll(async () => {
    await mongoose.connect('mongodb://localhost/feedback_test', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
  });

  afterAll(async () => {
    await mongoose.connection.db.dropDatabase();
    await mongoose.connection.close();
  });

  it('should submit feedback successfully', async () => {
    const res = await request(app)
      .post('/api/feedback')
      .send({
        textId: '12345',
        feedback: 1,
        userId: 'user_1',
      });
    expect(res.statusCode).toEqual(201);
    expect(res.body).toHaveProperty('message', 'Feedback submitted successfully.');
  });

  it('should return error for invalid feedback value', async () => {
    const res = await request(app)
      .post('/api/feedback')
      .send({
        textId: '12345',
        feedback: 2, // Invalid feedback
      });
    expect(res.statusCode).toEqual(400);
    expect(res.body).toHaveProperty('message', 'Invalid feedback value.');
  });
}); 