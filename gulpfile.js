var gulp            = require('gulp');
var argv            = require('yargs').argv;
var autoprefixer    = require('gulp-autoprefixer');
var bless           = require('gulp-bless');
var browserSync     = require('browser-sync').create();
var cssNano         = require('gulp-cssnano');
var del             = require('del');
var glob            = require('glob');
var gulpif          = require('gulp-if');
var svgmin          = require('gulp-svgmin');
var grunticon       = require('grunticon-lib');
var pixrem          = require('gulp-pixrem');
var plumber         = require('gulp-plumber');
var runSequence     = require('run-sequence');
var sass            = require('gulp-sass');
var sassLint        = require('gulp-sass-lint');
var sassGlob        = require('gulp-sass-glob');
var watch           = require('gulp-watch');
var bourbon         = require('bourbon').includePaths;
var uglify          = require('gulp-uglify');
var concat          = require('gulp-concat');

/* =================================== */
/* *** constants *** */

var srcPath = 'nurseconnect/static/src';
var distPath = 'nurseconnect/static/dist';
var templatesPath = 'nurseconnect/templates';

var production = argv.production >= 1;

var sassConfig = {
    includePaths: [
        'node_modules/breakpoint-sass/stylesheets/'
    ].concat(bourbon),
    outputStyle: 'compressed'
};


/* =================================== */
/* *** JS *** */
gulp.task('scripts', function() {
    return gulp.src(srcPath + '/js/**/*.js')
        .pipe(concat('main.js'))
        .pipe(uglify())
        .pipe(gulp.dest(distPath + '/js'));
});


/* =================================== */
/* *** SASS *** */

gulp.task('styles', ['clean-css', 'lint-sass'], function () {
    return gulp.src(srcPath + '/sass/**/*.s+(a|c)ss')
    .pipe(plumber())
    .pipe(sassGlob())
    .pipe(sass(sassConfig).on('error', sass.logError))
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
    .pipe(gulp.dest(distPath + '/css'))
    .pipe(browserSync.stream());
});

gulp.task('clean-css', function() {
    return del(distPath + '/css');
});

gulp.task('lint-sass', function() {
    return gulp.src(srcPath + '/**/*.s+(a|c)ss')
        .pipe(sassLint())
        .pipe(sassLint.format())
        .pipe(sassLint.failOnError());
});

/* =================================== */
/* *** Watch *** */
gulp.task('watch', function() {
    gulp.watch(srcPath + '/js/**/*.js', ['scripts']);
    gulp.watch(srcPath + '/sass/**/*.s+(a|c)ss', ['styles']);
});

/* =================================== */
/* *** generate iconset *** */

gulp.task('clean-generated-icons', function() {
    return del(srcPath + '/img/generated-icons');
});

gulp.task('clean-icons', function() {
    return del(distPath + '/icons');
});

gulp.task('crush-svgs', ['clean-generated-icons'], function () {
    return gulp.src(srcPath + '/img/svgs/*.svg')
        .pipe(svgmin())
        .pipe(gulp.dest(srcPath + '/img/generated-icons'));
});

gulp.task('icons', ['clean-icons', 'crush-svgs'], function (done) {
    var icons = glob.sync(srcPath + '/img/generated-icons/*.*');
    var options = {
        dynamicColorOnly: true,
        colors: {
            orangeBittersweet: '#ff6655',
            bluePelorous: '#2d9ec5',
            blueRegal: '#213d55',
            white: '#ffffff'
        }
    };

    var iconsTask = new grunticon(icons, distPath + '/icons', options);

    iconsTask.process(done);
});
/* =================================== */
/* *** sync browser *** */


// Static server
gulp.task('browser-sync', function() {
    browserSync.init({
        'proxy': 'localhost:8000/'
    });

    gulp.watch(srcPath + '/**/*.s+(a|c)ss', ['styles']);
    gulp.watch(templatesPath + '/**/*.html').on('change', browserSync.reload);
});

/* =================================== */
/* *** Default tasks *** */

gulp.task('default', ['clean-css'], function() {
    runSequence('styles', 'scripts','icons');
});
