module.exports = function (grunt) {
    'use strict';

    // Load grunt tasks automatically
    require('load-grunt-tasks')(grunt);

    // Time how long tasks take. Can help when optimizing build times
    require('time-grunt')(grunt);

    // Project configuration
    grunt.initConfig({
        // Metadata
        pkg: grunt.file.readJSON('package.json'),
        app: {
            public_root: 'static',
            frontend_path: 'frontend/',
            bower_path: require('./bower.json').appPath || 'frontend/',
        },

        jshint: {
            options: {
                jshintrc: true
            },
            gruntfile: {
                src: 'gruntfile.js'
            },
        },

        // Empties folders to start fresh
        clean: {
          css: {
            files: [{
              dot: true,
              src: [
                '<%=app.public_root %>/css/*'
              ]
            }]
          }
        },

        // Build all scss styles
        sass: {
            libs: {
                files: [{
                    expand: true,
                    cwd: '<%=app.frontend_path %>',
                    src: ['scss/libs/*.scss'],
                    dest: '<%=app.public_root %>/css/libs/',
                    ext: '.css',
                    flatten: true
                }]
            },
            dev: {
              options: {
                sourcemap: true,
              },
              files: [{
                expand: true,
                cwd: '<%=app.frontend_path %>',
                src: ['scss/user/*.scss'],
                dest: '<%=app.public_root %>/css/user/',
                ext: '.css',
                flatten: true
              }]
            }
        },

        watch: {
            libs: {
                files: '<%=app.frontend_path %>scss/libs/**',
                tasks: ['css-libs']
            },
            dev: {
                files: ['<%=app.frontend_path %>scss/user/**'],
                tasks: ['css-user']
            },
            gruntfile: {
                files: '<%= jshint.gruntfile.src %>',
                tasks: ['jshint:gruntfile']
            }
        },
    });

    grunt.registerTask('build', ['sass:libs', 'sass:dev']);
    grunt.registerTask('css-user', ['sass:dev']);
    grunt.registerTask('css-libs', ['sass:libs']);
    grunt.registerTask('css', ['css-libs', 'css-user']);
    grunt.registerTask('default', ['jshint', 'clean', 'css', 'watch']);
};

