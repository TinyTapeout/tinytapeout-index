// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 Tiny Tapeout B.V.
// Author: Uri Shaked

import { getAnalogPinLabels } from '../../../model/analog_pinouts';
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

  return {
    ...projectInfo,
    analog_pin_labels: getAnalogPinLabels(shuttle, projectInfo.analog_pins),
  };
});
