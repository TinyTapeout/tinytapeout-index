// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

export default eventHandler(async (event) => {
  const { fields } = getQuery(event);

  const shuttle = event.context.params.shuttle;
  if (!shuttle.endsWith('.json')) {
    throw createError({
      status: 404,
      message: 'Not found',
    });
  }

  const slug = shuttle.slice(0, -5);
  const cacheBuster = Date.now();
  const response = await fetch(
    `https://raw.githubusercontent.com/TinyTapeout/tinytapeout-index/main/index/${slug}.json?token=${cacheBuster}`,
  );
  if (!response.ok) {
    throw createError({
      status: 404,
      message: 'Not found',
    });
  }
  const index = await response.json();

  if (fields && typeof fields === 'string') {
    index.projects = index.projects.map((project) => {
      const newProject = {
        macro: project.macro,
      };
      for (const field of fields.split(',')) {
        newProject[field] = project[field];
      }
      return newProject;
    });
  }

  return index;
});
