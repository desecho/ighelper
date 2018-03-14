'use strict';

import Vue from 'vue';
import axios from 'axios';


window.vm = new Vue({
  el: '#app',
  data: {
    medias: vars.medias,
  },
  methods: {
    load: function() {
      function success(response) {
        if (response.data.status === 'success') {
          vm.flash(gettext('Medias have been loaded'), 'success', vars.flashOptions);
          vm.medias = response.data.medias;
        }
      }

      function fail() {
        vm.flash(gettext('Error loading medias'), 'error', vars.flashOptions);
      }

      const vm = this;
      axios.post(urls.loadMedias).then(success).catch(fail);
    },
    update: function(media) {
      function success(response) {
        if (response.data.status === 'success') {
          const updatedMedia = response.data.media;
          media.noLocation = updatedMedia.noLocation;
          media.noText = updatedMedia.noText;
          media.noTags = updatedMedia.noTags;
        }
      }

      function fail() {
        vm.flash(gettext('Error updating media'), 'error', vars.flashOptions);
      }

      const vm = this;
      const url = `${urls.media}${media.id}/update/`;
      axios.put(url).then(success).catch(fail);
    },
    hasIssue: function(media){
      return media.noText || media.noTags || media.noLocation
    }
  },
});