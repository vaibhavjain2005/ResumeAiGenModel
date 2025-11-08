// tailwind.config.js
const { heroui } = require("@heroui/theme");

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./node_modules/@heroui/theme/dist/components/(button|card|chip|date-input|divider|drawer|dropdown|form|image|input|input-otp|link|navbar|number-input|radio|select|ripple|spinner|modal|menu|popover|listbox|scroll-shadow).js",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
    },
  },
  darkMode: "class",
  plugins: [heroui()],
};