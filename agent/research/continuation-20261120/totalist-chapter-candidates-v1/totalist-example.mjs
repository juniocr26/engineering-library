import { totalist } from 'totalist';
const relativePaths = [];
await totalist('src', (relativePath, absolutePath, stats) => {
  relativePaths.push(relativePath);
});
// Illustrative only: no particular result set or order is asserted.
