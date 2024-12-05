// SPDX-License-Identifier: Apache-2.0
// Copyright 2024 Tiny Tapeout LTD
// Author: Uri Shaked

import YAML from 'yaml';
import { getProjectBaseUrl, oldDocsShuttles } from '../../../../model/shuttle';

export default eventHandler(async (event) => {
  const { shuttle, macro } = event.context.params;

  const projectUrl = getProjectBaseUrl(shuttle, macro);
  if (!projectUrl) {
    throw createError({ status: 404, message: 'Not found' });
  }

  if (!oldDocsShuttles.includes(shuttle)) {
    const infoUrl = `${projectUrl}/docs/info.md`;
    const response = await fetch(infoUrl);
    if (!response.ok) {
      throw createError({ status: 404, message: 'Not found' });
    }
    const text = await response.text();
    return new Response(text, {
      headers: {
        'content-type': 'text/markdown',
      },
    });
  }

  const infoUrl = `${projectUrl}/info.yaml`;
  const response = await fetch(infoUrl);
  if (!response.ok) {
    throw createError({ status: 404, message: 'Not found' });
  }
  const yamlText = await response.text();
  let infoYaml: {
    documentation: {
      how_it_works: string;
      how_to_test: string;
      external_hw: string;
      picture: string;
    };
  };
  try {
    infoYaml = YAML.parse(yamlText, { intAsBigInt: true });
  } catch (e) {
    throw createError({ status: 500, message: 'Failed to parse project YAML' });
  }
  const documentation = infoYaml.documentation;
  let markdown = `## How it works\n\n${documentation.how_it_works}\n\n`;
  markdown += `## How to test\n\n${documentation.how_to_test}\n\n`;
  if (documentation.external_hw) {
    markdown += `## External hardware\n\n${documentation.external_hw}\n\n`;
  }
  if (documentation.picture) {
    const extension = documentation.picture.split('.').pop();
    markdown += `![Picture](picture.${extension})\n\n`;
  }

  return new Response(markdown, {
    headers: {
      'content-type': 'text/markdown',
    },
  });
});
