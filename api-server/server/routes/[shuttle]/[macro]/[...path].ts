// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import { getProjectBaseUrl } from '../../../model/shuttle';

export default eventHandler(async (event) => {
  const { shuttle, macro, path } = event.context.params;
  const projectUrl = getProjectBaseUrl(shuttle, macro);
  if (!projectUrl) {
    throw createError({ status: 404, message: 'Not found' });
  }

  const cacheBuster = Date.now();
  const infoUrl = `${projectUrl}/${path}?token=${cacheBuster}`;
  return await fetch(infoUrl);
});
