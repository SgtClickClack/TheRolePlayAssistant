import { generateStory } from '../ai/story_generator';

test('generateStory returns a non-empty string', async () => {
  const prompt = 'Once upon a time,';
  const story = await generateStory(prompt);
  expect(typeof story).toBe('string');
  expect(story.length).toBeGreaterThan(0);
}); 