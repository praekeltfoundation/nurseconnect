let gulp            = require('gulp'),
 argv            = require('yargs').argv,
 autoprefixer    = require('gulp-autoprefixer'),
 bless           = require('gulp-bless'),
 browserSync     = require('browser-sync').create(),
 cssNano         = require('gulp-cssnano'),
 del             = require('del'),
 glob            = require('glob'),
 gulpif          = require('gulp-if'),
 svgmin          = require('gulp-svgmin'),
 pixrem          = require('gulp-pixrem'),
 plumber         = require('gulp-plumber'),
 sass            = require('gulp-sass'),
 sassLint        = require('gulp-sass-lint'),
 sassGlob        = require('gulp-sass-glob'),
 watch           = require('gulp-watch'),
 bourbon         = require('bourbon').includePaths,
 uglify          = require('gulp-uglify'),
 concat          = require('gulp-concat');

let srcPath = 'nurseconnect/static/src',
  distPath = 'nurseconnect/static/dist',
 templatesPath = 'nurseconnect/templates';

var production = argv.production >= 1;

/* ================JS=================== */

gulp.task('scripts', function() {
  return gulp.src('nurseconnect/static/src/js/**/*.js')
    .pipe(concat('index.js'))
    .pipe(uglify())
    .pipe(gulp.dest('nurseconnect/static/js'));
});


/* ==============SASS===================== */

gulp.task('clean-css', function() {
  return del('nurseconnect/static/css');
});

gulp.task('lint-sass', function() {
  return gulp.src(srcPath + '/**/*.s+(a|c)ss')
    .pipe(sassLint())
    .pipe(sassLint.format())
    .pipe(sassLint.failOnError());
});
gulp.task('styles', gulp.series('clean-css', function () {
  return gulp.src(srcPath + '/sass/**/*.s+(a|c)ss')
  .pipe(plumber())
  .pipe(sassGlob())
  .pipe(sass().on('error', sass.logError))
  .pipe(bless())
  .pipe(gulpif(production, autoprefixer({
    browsers: [
      'ie >= 8',
      'android >= 2.3',
      'iOS >= 6',
      '> 0%'
    ]
  })))
  .pipe(pixrem())
  .pipe(cssNano())
  .pipe(plumber.stop())
  .pipe(gulp.dest('nurseconnect/static/css'))
  .pipe(browserSync.stream());
}));



/* ================Generate Iconset=================== */

gulp.task('clean-generated-icons', function() {
  return del('nurseconnect/static/images/generated-icons');
});

gulp.task('crush-svgs', gulp.series('clean-generated-icons', function () {
  return gulp.src('nurseconnect/static/images/svgs/*.svg')
    .pipe(svgmin())
    .pipe(gulp.dest('nurseconnect/static/images/generated-icons'));
}));

gulp.task('clean-icons', function() {
  return del('nurseconnect/static/images/icons');
});

gulp.task('icons', gulp.series('clean-icons', 'crush-svgs', function (done) {
  var icons = glob.sync('nurseconnect/static/images/generated-icons/*.*');
  var options = {
    dynamicColorOnly: true,
    colors: {
        orangeBittersweet: '#ff6655',
        bluePelorous: '#2d9ec5',
        blueRegal: '#213d55',
        white: '#ffffff',
        black: '#000000'
    }
  };
}));
/* ==============Static server===================== */

gulp.task('browser-sync', function() {
  browserSync.init({
      'proxy': 'localhost:8000/'
  });
  gulp.watch(srcPath + '/**/*.s+(a|c)ss', ['styles']);
  gulp.watch(templatesPath + '/**/*.html').on('change', browserSync.reload);
});


/* ================Watch=================== */

gulp.task('watch', function() {
    gulp.watch(srcPath + '/js/**/*.js', ['scripts']);
    gulp.watch(srcPath + '/sass/**/*.s+(a|c)ss', ['styles']);
});

/* ================Default=================== */

gulp.task('default', gulp.series('styles','scripts','icons'));
