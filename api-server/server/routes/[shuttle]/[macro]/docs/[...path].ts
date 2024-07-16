// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import { getProjectBaseUrl, oldDocsShuttles } from '../../../../model/shuttle';

export default eventHandler(async (event) => {
  const { shuttle, macro, path } = event.context.params;
  const projectUrl = getProjectBaseUrl(shuttle, macro);
  if (!projectUrl) {
    throw createError({ status: 404, message: 'Not found' });
  }

  const cacheBuster = Date.now();

  if (oldDocsShuttles.includes(shuttle)) {
    if (!path.startsWith('picture.')) {
      throw createError({ status: 404, message: 'Not found' });
    }
    return await fetch(`${projectUrl}/${path}?token=${cacheBuster}`);
  }

  return await fetch(`${projectUrl}/docs/${path}?token=${cacheBuster}`);
});
