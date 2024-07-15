// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import { loadShuttleIndex } from '../../../model/shuttle';

export default eventHandler(async (event) => {
  const { shuttle, macro: macroPath } = event.context.params;
  if (!macroPath.endsWith('.json')) {
    throw createError({ status: 404, message: 'Not found' });
  }
  const macro = macroPath.slice(0, -5);
  
  const index = await loadShuttleIndex(shuttle);
  if (!index) {
    throw createError({ status: 404, message: 'Not found' });
  }
  
  const projectInfo = index.projects.find((project) => project.macro === macro);
  if (!projectInfo) {
    throw createError({ status: 404, message: 'Not found' });
  }

  return projectInfo;
});
