<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  filters: Filters
  settings_header: Settings profiles
  load_profile: Select profile
  save_as: Save as...
  create_success: New settings profile created successfully
  update_success: Settings profile updated successfully
  profile_name: Settings profile name
  name_empty: Profile name is required
  save: Save
  export_csv: Export .csv
  cancel: Cancel
  publishers_selected: Publishers selected
  langs_selected: Languages selected
  subjects_selected: Subjects selected
  create_profile: Create new profile
  save_settings: Save current setting under the same name
  clean_filters: Remove filters
  yop_from: Publication year - from
  yop_to: Publication year - to
  yop: Publication year
cs:
  filters: Filtry
  settings_header: Profily nastavení
  load_profile: Vyběr profilu
  save_as: Uložit jako...
  create_success: Nový profil nastavení byl úspěšně vytvořený
  update_success: Profil nastavení byl úspěšně uložen
  profile_name: Jméno profilu nastavení
  name_empty: Je vyžadováno jméno profilu nastavení
  save: Uložit
  export_csv: Export .csv
  cancel: Cancel
  publishers_selected: Vybraní vydavatelé
  langs_selected: Vybrané jazyky
  subjects_selected: Vybraná témata
  create_profile: Vytvořit nový profil
  save_settings: Uložit současné nastavení pod stejným jménem
  clean_filters: Odstranit filtry
  yop_from: Rok vydání - od
  yop_to: Rok vydání - do
  yop: Rok vydání
</i18n>

<template>
  <v-container fluid>
    <v-row justify="space-between">
      <v-col cols="auto" class="py-0">
        <v-card elevation="0">
          <v-card-text class="pb-0 d-flex">
            <span class="mt-2 mr-3 black-button text--primary"
              >{{ $t("settings_header") }}:</span
            >
            <v-tooltip bottom>
              <template #activator="{ on }">
                <v-btn
                  icon
                  class=""
                  top
                  color="blue lightgreen-2"
                  :disabled="saveDisabled"
                  @click="saveSelectedProfile()"
                  v-on="on"
                >
                  <v-icon>fas fa-save</v-icon>
                </v-btn>
              </template>
              {{ $t("save_settings") }}
            </v-tooltip>
            <v-select
              v-model="selectedProfile"
              :items="settingsProfiles"
              item-value="pk"
              item-text="name"
              :label="$t('load_profile')"
              class="mr-3"
              dense
            >
            </v-select>
            <v-btn
              color="info"
              outlined
              @click="createDialog = !createDialog"
              small
            >
              {{ $t("save_as") }}
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="auto" class="py-0">
        <v-btn
          v-if="exportUrl"
          color="success"
          class="mt-3"
          :href="exportUrl"
          target="_blank"
        >
          {{ $t("export_csv") }}
        </v-btn>
      </v-col>
    </v-row>

    <v-row>
      <v-col :cols="12">
        <v-expansion-panels>
          <v-expansion-panel>
            <v-expansion-panel-header>
              <template v-slot:default="{ open }">
                <v-row no-gutters class="align-center">
                  <v-col cols="3">
                    {{ $t("filters") }}
                  </v-col>
                  <v-col cols="6" v-if="!open">
                    <span class="pe-4">
                      <span class="font-weight-light">{{ $t("yop") }}:</span>
                      {{ yopFrom && !yopTo ? ">" : "" }}
                      {{ yopFrom || "" }}
                      {{
                        yopFrom && yopTo
                          ? "&ndash;"
                          : yopFrom
                          ? ""
                          : yopTo
                          ? "<"
                          : "-"
                      }}
                      {{ yopTo || "" }}
                    </span>
                    <span class="pe-4">
                      <span class="font-weight-light"
                        >{{ $t("publishers_selected") }}:</span
                      >
                      {{ selectedPublishers.length }}
                    </span>
                    <span class="pe-4">
                      <span class="font-weight-light"
                        >{{ $t("langs_selected") }}:</span
                      >
                      {{ selectedLangs.length }}
                    </span>
                    <span class="pe-4">
                      <span class="font-weight-light"
                        >{{ $t("subjects_selected") }}:</span
                      >
                      {{ selectedTopics.length }}
                    </span>
                  </v-col>
                  <v-col cols="3">
                    <v-btn
                      v-if="filtersApplied"
                      small
                      @click.stop="cleanFilters()"
                    >
                      <v-icon small class="mr-1" color="#555555"
                        >fa fa-times</v-icon
                      >
                      {{ $t("clean_filters") }}
                    </v-btn>
                  </v-col>
                </v-row>
              </template>
            </v-expansion-panel-header>
            <v-expansion-panel-content eager>
              <v-row>
                <v-col cols="auto" class="pb-0">
                  <v-text-field
                    type="number"
                    v-model.number="yopFromDebounced"
                    :label="$t('yop_from')"
                    clearable
                    validate-on-blur
                  />
                </v-col>
                <v-col cols="auto" class="pb-0">
                  <v-text-field
                    type="number"
                    v-model.number="yopToDebounced"
                    :label="$t('yop_to')"
                    clearable
                  />
                </v-col>
              </v-row>
              <v-row>
                <v-col :cols="4">
                  <TopicsFilterTable
                    v-model="selectedPublishers"
                    urlArg="publisher"
                    :header="$t('columns.publisher')"
                    :candidate_count_filters="filters"
                    @ready="publishersReady = true"
                  />
                </v-col>
                <v-col :cols="3">
                  <TopicsFilterTable
                    v-model="selectedLangs"
                    urlArg="language"
                    :header="$t('pages.languages')"
                    :candidate_count_filters="filters"
                    @ready="langsReady = true"
                  />
                </v-col>
                <v-col :cols="5">
                  <SubjectTree
                    v-model="selectedTopics"
                    :height="'392px'"
                    :candidate_count_filters="filters"
                    score_type="candidates_count"
                    @ready="topicsReady = true"
                  />
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>

    <v-row>
      <v-col :col="12">
        <CandidatesTable
          v-if="childrenReady && profileLoaded"
          :filters="filters"
          :ordering.sync="ordering"
          :scoreYearIdx="scoreYearIdx"
          :scoreWeights="scoreWeights"
          :displayFilters="displayFilters"
          :formats.sync="formats"
          :yopFrom="yopFrom"
          :yopTo="yopTo"
          @export-url-update="updateExportUrl"
        />
        <v-card v-else>
          <v-card-title>{{ $t("pages.candidates") }}</v-card-title>
          <v-card-text>
            <v-skeleton-loader type="paragraph@5"></v-skeleton-loader>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="createDialog" max-width="500">
      <v-card>
        <v-card-title>
          {{ $t("create_profile") }}
        </v-card-title>
        <v-card-text>
          <v-text-field
            :label="$t('profile_name')"
            required
            v-model="newProfileName"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="createDialog = false">
            {{ $t("cancel") }}
          </v-btn>
          <v-btn color="primary" text @click="createSettingsProfile">
            {{ $t("save") }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import axios from "axios";
import CandidatesTable from "@/components/CandidatesTable";
import TopicsFilterTable from "@/components/TopicsFilterTable";
import SubjectTree from "@/components/SubjectTree";
import { mapActions } from "vuex";
import isArray from "lodash/isArray";
import isEqual from "lodash/isEqual";
import isEqualWith from "lodash/isEqualWith";
import isInteger from "lodash/isInteger";
import cloneDeep from "lodash/cloneDeep";
import debounce from "lodash/debounce";

function customArrayCompare(objValue, othValue) {
  if (isArray(objValue) && isArray(othValue) && isInteger(objValue[0]))
    return isEqual([...objValue].sort(), [...othValue].sort());
}

export default {
  name: "CandidatesTablePage",
  components: { CandidatesTable, TopicsFilterTable, SubjectTree },

  data() {
    return {
      selectedPublishers: [],
      selectedLangs: [],
      selectedTopics: [],
      settingsProfiles: [],
      defaultSettingsProfileId: null,
      namedSettingsProfile: null,
      scoreYearIdx: 5,
      scoreWeights: { authors: 1, publisher: 1, languages: 1, subjects: 1 },
      selectedProfile: null,
      createDialog: false,
      newProfileName: "",
      displayFilters: {
        showUnreviewed: true,
        showLiked: true,
        showDisliked: false,
      },
      ordering: { sortBy: ["score"], sortDesc: [true] },
      filterNames: ["publisher", "language", "psh"],
      yopFrom: null,
      yopTo: null,
      formats: [],
      lastSavedDefault: null,
      readyWatcherUnwatch: null,
      langsReady: false,
      publishersReady: false,
      topicsReady: false,
      exportUrl: null,
      profileLoaded: false,
    };
  },

  computed: {
    filters() {
      let out = {};
      if (this.selectedTopics.length)
        out["psh"] = [...this.selectedTopics].sort();
      if (this.selectedLangs.length)
        out["language"] = [...this.selectedLangs].sort();
      if (this.selectedPublishers.length)
        out["publisher"] = [...this.selectedPublishers].sort();
      return out;
    },
    settingsProfile() {
      return {
        filters: this.filters,
        weights: this.scoreWeights,
        scoreYearIdx: this.scoreYearIdx,
        displayFilters: this.displayFilters,
        ordering: this.ordering,
        formats: this.formats,
        yopFrom: this.yopFrom,
        yopTo: this.yopTo,
      };
    },
    saveDisabled() {
      if (this.selectedProfileObject) {
        return isEqualWith(
          this.settingsProfile,
          this.selectedProfileObject.settings_obj,
          customArrayCompare
        );
      }
      return true;
    },
    selectedProfileObject() {
      if (this.selectedProfile) {
        return this.settingsProfiles.find(
          (item) => item.pk === this.selectedProfile
        );
      }
      return null;
    },
    childrenReady() {
      return this.langsReady && this.topicsReady && this.publishersReady;
    },
    filtersApplied() {
      return (
        this.selectedPublishers.length ||
        this.selectedLangs.length ||
        this.selectedTopics.length
      );
    },
    yopFromDebounced: {
      get() {
        return this.yopFrom;
      },
      set: debounce(function (value) {
        this.yopFrom = value;
      }, 500),
    },
    yopToDebounced: {
      get() {
        return this.yopTo;
      },
      set: debounce(function (value) {
        this.yopTo = value;
      }, 500),
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    saveSelectedProfile() {
      this.saveSettingsProfile(this.selectedProfile);
    },
    async loadAllProfiles(applyDefault) {
      try {
        const resp = await axios.get("/api/candidates_settings/");
        this.settingsProfiles = [];
        resp.data.forEach((el) => {
          if (el.name === "default" && el.internal) {
            this.defaultSettingsProfileId = el.pk;
            if (applyDefault) {
              if (this.childrenReady) {
                this.updateSettings(el);
                this.profileLoaded = true;
              } else {
                this.readyWatcherUnwatch = this.$watch("childrenReady", () => {
                  this.updateSettings(el);
                  if (this.readyWatcherUnwatch) {
                    this.readyWatcherUnwatch();
                  }
                  this.profileLoaded = true;
                });
              }
            }
          } else {
            this.settingsProfiles.push(el);
          }
        });
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching candidates settings profiles: " + error,
          color: "error",
        });
      }
    },
    async saveDefaultSettingsProfile() {
      this.lastSavedDefault = cloneDeep(this.settingsProfile);
      await axios.put(
        `/api/candidates_settings/${this.defaultSettingsProfileId}/`,
        {
          name: "default",
          settings_obj: this.lastSavedDefault,
        }
      );
    },
    async saveSettingsProfile(profileId) {
      const profileObj = this.settingsProfiles.find(
        (item) => item.pk === profileId
      );
      try {
        const resp = await axios.put(`/api/candidates_settings/${profileId}/`, {
          name: profileObj.name,
          settings_obj: this.settingsProfile,
        });
        this.selectedProfile = resp.data.pk;
        this.$set(profileObj, "settings_obj", resp.data.settings_obj);
        this.showSnackbar({
          content: this.$i18n.t("update_success"),
          color: "success",
        });
      } catch (error) {
        this.showSnackbar({
          content: "Error updating candidates settings profile: " + error,
          color: "error",
        });
      }
    },
    async createSettingsProfile() {
      if (!this.newProfileName) {
        this.showSnackbar({
          content: this.$i18n.t("name_empty"),
          color: "error",
        });
        return null;
      }
      try {
        const resp = await axios.post(`/api/candidates_settings/`, {
          name: this.newProfileName,
          settings_obj: this.settingsProfile,
        });
        if (resp.status === 201) {
          this.showSnackbar({
            content: this.$i18n.t("create_success"),
            color: "success",
          });
          this.settingsProfiles.push(resp.data);
          this.selectedProfile = resp.data.pk;
        }
      } catch (error) {
        this.showSnackbar({
          content: "Error updating candidates settings profile: " + error,
          color: "error",
        });
      } finally {
        this.createDialog = false;
      }
    },

    updateSettings(profile) {
      let profileObj = profile;
      if (profileObj.settings_obj) {
        this.scoreWeights = profileObj.settings_obj.weights;
        this.scoreYearIdx = profileObj.settings_obj.scoreYearIdx;
        this.selectedLangs = profileObj.settings_obj.filters?.language || [];
        this.selectedPublishers =
          profileObj.settings_obj.filters?.publisher || [];
        this.selectedTopics = profileObj.settings_obj.filters?.psh || [];
        this.displayFilters = profileObj.settings_obj.displayFilters;
        this.ordering = profileObj.settings_obj.ordering;
        this.formats = profileObj.settings_obj.formats;
        this.yopFrom = profileObj.settings_obj.yopFrom;
        this.yopTo = profileObj.settings_obj.yopTo;
      }
    },
    cleanFilters() {
      this.selectedLangs = [];
      this.selectedTopics = [];
      this.selectedPublishers = [];
    },
    updateExportUrl(value) {
      this.exportUrl = value;
    },
  },

  watch: {
    selectedProfile() {
      this.updateSettings(this.selectedProfileObject);
    },
    settingsProfile: {
      handler() {
        if (!isEqual(this.settingsProfile, this.lastSavedDefault))
          this.saveDefaultSettingsProfile();
      },
      deep: true,
    },
  },

  mounted() {
    this.loadAllProfiles(true);
  },
};
</script>
