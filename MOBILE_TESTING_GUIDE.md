# 📱 Mobile Testing Quick Guide

## Quick Test Checklist

### Before Deployment
- [ ] Test on actual mobile device (not just emulator)
- [ ] Check both portrait and landscape
- [ ] Verify touch targets (44px minimum)
- [ ] Test with slow 3G connection
- [ ] Check image loading and fallbacks

### Chrome DevTools Mobile Testing

#### Step 1: Open DevTools
```
Press F12 or Ctrl+Shift+I (Windows)
Press Cmd+Option+I (Mac)
```

#### Step 2: Enable Device Toolbar
```
Press Ctrl+Shift+M (Windows)
Press Cmd+Shift+M (Mac)
Or click the device icon in DevTools
```

#### Step 3: Test These Resolutions
```
Mobile S:  320px × 568px  (iPhone SE)
Mobile M:  375px × 667px  (iPhone 8)
Mobile L:  425px × 812px  (iPhone X)
Tablet:    768px × 1024px (iPad)
Laptop:    1024px × 768px (Desktop)
```

### Common Mobile Issues to Check

#### 1. Text Readability
```css
Minimum font size: 14px
Body text: 15-16px
Headers: 18-24px
```

#### 2. Touch Targets
```css
Minimum size: 44px × 44px
Spacing: 8px between elements
```

#### 3. Column Layouts
- Should stack vertically on mobile
- No horizontal scrolling
- Full width on small screens

#### 4. Images
- Should scale to container
- Maintain aspect ratio
- No overflow

#### 5. Forms
- Inputs: 16px font (prevents iOS zoom)
- Large enough to tap easily
- Proper keyboard types (email, tel, number)

### Test URLs

#### Localhost
```
http://localhost:8501
```

#### On Mobile Device (Same Network)
```
1. Find your computer's IP:
   - Windows: ipconfig
   - Mac/Linux: ifconfig

2. On mobile, visit:
   http://[YOUR_IP]:8501
   
Example: http://192.168.1.100:8501
```

#### Streamlit Cloud
```
https://your-app.streamlit.app
```

### Browser Testing Priority

#### High Priority (Most Users)
1. ✅ Safari iOS (iPhone)
2. ✅ Chrome Android
3. ✅ Chrome iOS

#### Medium Priority
4. ⚠️ Firefox Mobile
5. ⚠️ Samsung Internet
6. ⚠️ Edge Mobile

### Quick Fix Reference

#### Issue: Horizontal scroll on mobile
```python
st.markdown(\"\"\"
    <style>
    @media (max-width: 768px) {
        .main { overflow-x: hidden; }
    }
    </style>
\"\"\", unsafe_allow_html=True)
```

#### Issue: Columns not stacking
```python
st.markdown(\"\"\"
    <style>
    @media (max-width: 768px) {
        [data-testid=\"column\"] {
            width: 100% !important;
            min-width: 100% !important;
        }
    }
    </style>
\"\"\", unsafe_allow_html=True)
```

#### Issue: Images too large
```python
# Use this instead of fixed width
st.image(image, use_column_width=True)

# Or with display_image helper
from image_utils import display_image
display_image(image_url)  # Automatically responsive
```

#### Issue: Text too small
```python
st.markdown(\"\"\"
    <style>
    @media (max-width: 768px) {
        p, div, span { font-size: 15px !important; }
    }
    </style>
\"\"\", unsafe_allow_html=True)
```

#### Issue: Buttons too small to tap
```python
st.markdown(\"\"\"
    <style>
    button {
        min-height: 44px !important;
        padding: 12px 20px !important;
    }
    </style>
\"\"\", unsafe_allow_html=True)
```

### Performance Testing

#### Test Page Load Speed
```
1. Open DevTools Network tab
2. Set throttling to "Slow 3G"
3. Reload page
4. Check load time (should be < 5s)
```

#### Optimize Images
```python
# Use WebP format
# Compress before upload
# Lazy load off-screen images
```

### Accessibility Testing

#### Touch Target Size
```javascript
// Run in Console to find small tap targets
document.querySelectorAll('button, a, input').forEach(el => {
  const rect = el.getBoundingClientRect();
  if (rect.width < 44 || rect.height < 44) {
    console.warn('Small tap target:', el, rect);
  }
});
```

#### Color Contrast
```
Tool: Chrome Lighthouse
1. DevTools > Lighthouse
2. Select "Accessibility"
3. Generate report
4. Fix contrast issues
```

### Real Device Testing

#### iOS Devices
```
iPhone SE:      Small screen (4.7")
iPhone 14:      Standard (6.1")
iPhone 14 Pro:  Large (6.7")
iPad:           Tablet (10.2")
```

#### Android Devices
```
Samsung S-series
Google Pixel
Various screen sizes
```

### Common Streamlit Mobile Gotchas

1. **Sidebar**: May cover content on small screens
   - Test with sidebar collapsed
   - Ensure content accessible

2. **Dataframes**: Can be too wide
   - Use `st.dataframe(df, use_container_width=True)`
   - Or show subset of columns on mobile

3. **Charts**: Need explicit sizing
   - Plotly: `use_container_width=True`
   - Set reasonable min-height

4. **File Uploads**: Work differently on mobile
   - Test camera access
   - Test file picker

5. **Maps**: Performance can be slow
   - Consider simpler markers on mobile
   - Test zoom/pan gestures

### Emergency Fixes

#### If site is broken on mobile:

1. **Clear cache**: Settings > Clear browsing data
2. **Hard refresh**: Shift+F5 (desktop), force close app (mobile)
3. **Check console**: Look for JavaScript errors
4. **Disable custom CSS**: Comment out `apply_nature_theme()`
5. **Test in incognito**: Rules out extension issues

### Resources

- [Chrome DevTools Device Mode](https://developer.chrome.com/docs/devtools/device-mode/)
- [Apple HIG - Touch Targets](https://developer.apple.com/design/human-interface-guidelines/ios/visual-design/adaptivity-and-layout/)
- [Google Material Design - Touch](https://material.io/design/usability/accessibility.html#layout-and-typography)
- [Streamlit Responsive Layout](https://docs.streamlit.io/library/api-reference/layout)

### Support

If mobile issues persist:
1. Check `MOBILE_COMPATIBILITY_UPDATE.md`
2. Review `nature_theme.py` media queries
3. Test with minimal page (no custom CSS)
4. File issue with device/browser details

---

**Quick Test Command**:
```bash
streamlit run Home.py --server.port 8501
# Then visit from mobile on same network
```

**Remember**: Always test on real devices before production deployment!
