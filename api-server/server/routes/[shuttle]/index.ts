// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import {
  type IShuttleIndex,
  type IShuttleIndexProject,
  loadShuttleIndex,
} from '../../model/shuttle';

type IShuttleIndexPartial = Omit<IShuttleIndex, 'projects'> & {
  projects: Partial<IShuttleIndexProject>[];
};

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
  const index: IShuttleIndexPartial | null = await loadShuttleIndex(slug);
  if (!index) {
    throw createError({
      status: 404,
      message: 'Not found',
    });
  }

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
