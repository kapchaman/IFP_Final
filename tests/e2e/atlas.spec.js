import { test, expect } from '@playwright/test';

test('create, connect, explore, edit, persist, and delete ideas', async ({ page }) => {
  const suffix = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
  const first = `Atom ${suffix}`;
  const second = `Molecule ${suffix}`;
  const renamed = `Edited ${suffix}`;
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.atlasReady === 'true');
  await expect(page.getByRole('button', { name: 'Refresh atlas' })).toBeEnabled();
  async function create(title) {
    await page.getByRole('button', { name: '＋ New concept', exact: true }).click();
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    await modal.getByLabel('CONCEPT TITLE').fill(title);
    await modal.getByLabel('DESCRIPTION').fill('An idea for browser verification.');
    await modal.getByLabel('CATEGORY').fill('Browser checks');
    await modal.getByRole('button', { name: 'Save concept' }).click();
    await expect(modal).toHaveCount(0);
    await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible();
  }
  await create(first);
  await create(second);
  await page.getByRole('button', { name: '＋ Connect', exact: true }).click();
  let modal = page.getByRole('dialog');
  await modal.getByLabel('TARGET CONCEPT').selectOption({ label: first });
  await modal.getByLabel('RELATIONSHIP', { exact: true }).selectOption('Explains');
  await modal.getByLabel('NOTE (OPTIONAL)').fill('A useful relationship');
  await modal.getByRole('button', { name: 'Connect', exact: true }).click();
  await expect(page.getByText('A useful relationship')).toBeVisible();
  await page.getByRole('combobox', { name: 'Path starting concept' }).selectOption({ label: second });
  await page.getByRole('combobox', { name: 'Path destination concept' }).selectOption({ label: first });
  await page.getByRole('button', { name: 'Find path', exact: true }).click();
  await expect(page.getByText(`1 step(s): ${second} → ${first}`, { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Edit', exact: true }).click();
  modal = page.getByRole('dialog');
  await modal.getByLabel('CONCEPT TITLE').fill(renamed);
  await modal.getByRole('button', { name: 'Save concept' }).click();
  await expect(modal).toHaveCount(0);
  await page.reload();
  await page.waitForFunction(() => document.body.dataset.atlasReady === 'true');
  await page.getByRole('button', { name: 'Show library' }).click();
  await page.getByRole('button').filter({ has: page.getByText(renamed, { exact: true }) }).click();
  await expect(page.getByRole('heading', { name: renamed, exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Delete selected concept' }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Delete concept', exact: true }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await page.getByRole('button').filter({ has: page.getByText(first, { exact: true }) }).click();
  await expect(page.getByText('No connections yet.', { exact: false })).toBeVisible();
  await page.getByRole('button', { name: 'Delete selected concept' }).click();
  await page.getByRole('dialog').getByRole('button', { name: 'Delete concept', exact: true }).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  expect(errors).toEqual([]);
});

test('keyboard dialog dismissal and responsive width', async ({ page }) => {
  await page.goto('/');
  await page.waitForFunction(() => document.body.dataset.atlasReady === 'true');
  await expect(page.getByRole('button', { name: 'Refresh atlas' })).toBeEnabled();
  await page.getByRole('button', { name: '＋ New concept', exact: true }).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.getByRole('dialog')).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
