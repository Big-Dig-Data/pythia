<i18n>
en:
  input:
    search_placeholder: Start typing to search
    works_label: Works
  no_data: Sorry, but nothing matching was found
cs:
  input:
    search_placeholder: Pro vyhledávání začněte psát
    works_label: Díla
  no_data: Je nám to líto, ale nic odpovídajícího jsme nenašli
</i18n>

<template>
  <v-container fluid>
    <v-row>
      <v-col :cols="12" class="pa-1">
        <v-autocomplete
          v-model="selectedRecord"
          :items="records"
          :loading="isLoading"
          :search-input.sync="queryText"
          color="primary"
          item-text="name"
          item-value="pk"
          :label="$t('input.works_label')"
          :placeholder="$t('input.search_placeholder')"
          prepend-inner-icon="fa-search"
          return-object
          clearable
          clear-icon="fa-times"
          :no-filter="true"
        >
          <template v-slot:item="{ item }">
            <v-list-item-content>
              <v-list-item-title v-html="item.name"></v-list-item-title>
              <v-list-item-subtitle v-if="item.authors">
                <span
                  v-for="author in item.authors"
                  class="author"
                  :key="author.pk"
                >
                  {{ author.name }}
                </span>
              </v-list-item-subtitle>
            </v-list-item-content>
            <!--v-list-item-avatar>{{ item.score }}</v-list-item-avatar-->
          </template>
          <template v-slot:no-data>
            <div class="pa-2">
              <v-icon>fa-frown</v-icon>
              {{ $t("no_data") }}
            </div>
          </template>
        </v-autocomplete>
      </v-col>
    </v-row>

    <v-row v-if="workIdToShow">
      <v-col>
        <WorkDetail :work-id="workIdToShow" :key="workIdToShow" />
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="6">
        <TopItemsWidget order-by="score" itemType="work" />
      </v-col>
      <v-col cols="6">
        <TopItemsWidget
          order-by="new_works_acquisition_score"
          itemType="work"
          :includeInfo="true"
        />
      </v-col>

      <v-col cols="12">
        <WorksGrowthOverview />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import WorkDetail from "../components/WorkDetail";

import axios from "axios";
import debounce from "lodash/debounce";
import { mapActions, mapGetters } from "vuex";
import TopItemsWidget from "../components/TopItemsWidget";
import WorksGrowthOverview from "../components/WorksGrowthOverview";

export default {
  name: "WorkDetailPage",
  components: { WorkDetail, TopItemsWidget, WorksGrowthOverview },
  props: {
    workId: { required: false },
  },
  data() {
    return {
      records: [],
      selectedRecord: null,
      isLoading: false,
      queryText: "",
    };
  },
  computed: {
    ...mapGetters({
      chartColors: "chartColors",
    }),
    selectedWorksetUUID() {
      const workset = this.$store.getters.selectedWorkset;
      if (workset) return workset.uuid;
      return null;
    },
    workIdToShow() {
      if (this.workId) {
        return this.workId;
      }
      if (this.selectedRecord) {
        return this.selectedRecord.pk;
      }
      return null;
    },
  },
  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    debouncedLoadMatchingWorks: debounce(function () {
      this.loadMatchingWorks();
    }, 500),
    async loadMatchingWorks() {
      if (this.selectedWorksetUUID) {
        this.isLoading = true;
        try {
          const response = await axios.get(
            `/api/bookrank/workset/${this.selectedWorksetUUID}/works/`,
            { params: { q: this.queryText } }
          );
          this.records = response.data.results;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching data: " + error,
            color: "error",
          });
          console.log("Error fetching data", error);
        } finally {
          this.isLoading = false;
        }
      }
    },
  },
  watch: {
    queryText() {
      this.debouncedLoadMatchingWorks();
    },
    selectedRecord() {
      if (this.selectedRecord) {
        this.$router.push({
          name: "work detail",
          params: { workId: this.selectedRecord.pk },
        });
      } else {
        this.$router.push({ name: "work detail root" });
      }
    },
  },
};
</script>

<style lang="scss">
.author {
  font-size: 75%;
  color: #666666;

  &:after {
    content: ";";
    margin-right: 0.35rem;
  }

  &:last-child {
    &:after {
      content: "";
    }
  }
}
div.loader {
  width: 400px;
  height: 400px;
  text-align: center;
  padding-top: 100px;
  //border: solid 1px #eeeeee;
  border-radius: 5px;
  background: rgba(227, 252, 249, 0.25);

  span.fas {
    color: var(--v-primary-base);
  }
}
</style>
