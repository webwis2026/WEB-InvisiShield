#!/usr/bin/env node
/**
 * 零改造引擎插件配置校验脚本
 * 1. JSON Schema 结构校验（需配合 plugin-config.schema.json）
 * 2. 自定义业务规则校验（插件顺序、禁止项等）
 *
 * 使用: node plugin-validate.js <config.json>
 * 或: npx ajv validate -s plugin-config.schema.json -d examples/gitlab_config.json
 */

const fs = require('fs');
const path = require('path');

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function getPluginName(item) {
  return typeof item === 'string' ? item : item?.name;
}

function validateCustomRules(data) {
  const errors = [];
  const gw = data.gw_configures;
  if (!gw) return errors;

  const plugins = gw.plugins || [];
  const exposureAuthIndex = plugins.findIndex(
    (p) => getPluginName(p) === 'exposure_auth'
  );

  // 若含 exposure_auth，检查 uri_blocker、request_blocker、uri_bypass 顺序
  if (exposureAuthIndex >= 0) {
    const beforeAuth = plugins.slice(0, exposureAuthIndex).map(getPluginName);
    if (!beforeAuth.includes('uri_blocker')) {
      errors.push({
        rule: 'plugin_order',
        message: 'uri_blocker 必须在 exposure_auth 之前',
        path: 'gw_configures.plugins',
      });
    }
    if (!beforeAuth.includes('request_blocker')) {
      errors.push({
        rule: 'plugin_order',
        message: 'request_blocker 必须在 exposure_auth 之前',
        path: 'gw_configures.plugins',
      });
    }
    if (!beforeAuth.includes('uri_bypass')) {
      errors.push({
        rule: 'plugin_order',
        message: 'uri_bypass 必须在 exposure_auth 之前',
        path: 'gw_configures.plugins',
      });
    }
  }

  // 禁止 regex_whiteuri
  const hasRegexWhiteuri = plugins.some((p) => getPluginName(p) === 'regex_whiteuri');
  if (hasRegexWhiteuri) {
    errors.push({
      rule: 'forbidden',
      message: '禁止使用 regex_whiteuri，请改用 uri_bypass',
      path: 'gw_configures.plugins',
    });
  }

  // 禁止 exposure_session、exposure_user 在主 plugins
  const forbiddenInPlugins = ['exposure_session', 'exposure_user'];
  for (const name of forbiddenInPlugins) {
    if (plugins.some((p) => getPluginName(p) === name)) {
      errors.push({
        rule: 'forbidden',
        message: `${name} 必须在 plugin_confs 中配置，不得在主 plugins 数组`,
        path: 'gw_configures.plugins',
      });
    }
  }

  // 子路由禁止 plugin_group_id（新规范）
  const subRoutes = gw.sub_routes || [];
  for (let i = 0; i < subRoutes.length; i++) {
    const sr = subRoutes[i];
    if (sr.plugin_group_id && !sr.plugins) {
      errors.push({
        rule: 'deprecated',
        message: `sub_routes[${i}] 使用 plugin_group_id，新规范建议使用内联 plugins`,
        path: `gw_configures.sub_routes[${i}]`,
      });
    }
  }

  // 禁止 plugin_groups
  if (gw.plugin_groups && Object.keys(gw.plugin_groups).length > 0) {
    errors.push({
      rule: 'forbidden',
      message: 'plugin_groups 已废弃，请使用子路由内联 plugins',
      path: 'gw_configures.plugin_groups',
    });
  }

  return errors;
}

function main() {
  const configPath = process.argv[2];
  if (!configPath) {
    console.error('Usage: node plugin-validate.js <config.json>');
    process.exit(1);
  }

  const fullPath = path.resolve(configPath);
  if (!fs.existsSync(fullPath)) {
    console.error('File not found:', fullPath);
    process.exit(1);
  }

  let data;
  try {
    data = loadJson(fullPath);
  } catch (e) {
    console.error('JSON parse error:', e.message);
    process.exit(1);
  }

  const customErrors = validateCustomRules(data);
  if (customErrors.length > 0) {
    console.error('Validation failed:\n');
    customErrors.forEach((e) => {
      console.error(`  [${e.rule}] ${e.path}: ${e.message}`);
    });
    process.exit(1);
  }

  console.log('Custom rules: OK');
  console.log('Note: Run JSON Schema validation with: npx ajv validate -s plugin-config.schema.json -d', configPath);
}

main();
